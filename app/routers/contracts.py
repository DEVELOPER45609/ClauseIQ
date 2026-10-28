import shutil
from pathlib import Path
from fastapi import APIRouter, Depends, File, UploadFile, BackgroundTasks, HTTPException,status
from sqlmodel import Session

from app.core.config import settings
from app.core.database import get_session,engine
from app.core.deps import get_current_user
from app.models.user import User
from app.models.contract import Contract
from app.rag.ingestion import ingest_contract
from app.schemas.contract import ContractStatus, ContractRead

router = APIRouter(prefix="/api/contracts", tags=["contracts"])

UPLOAD_DIR = Path(settings.UPLOAD_DIR)
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

def _process_contract(contract_id: int, file_path: str, owner_id: int):
    """Background task — apna alag DB session, jaisa SmartDesk ke triage_ticket me tha."""
    with Session(engine) as session:
        contract = session.get(Contract, contract_id)
        try:
            doc_id, clause_count = ingest_contract(file_path, owner_id)
            contract.doc_id = doc_id
            contract.clause_count = clause_count
            contract.status = "completed"
        except Exception as e:
            contract.status = "failed"
            contract.error_message = str(e)
        session.add(contract)
        session.commit()


@router.post("/", response_model=ContractRead, status_code=status.HTTP_201_CREATED)
def upload_contract(
    file: UploadFile,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    temp_path = UPLOAD_DIR / f"{current_user.id}_{file.filename}"
    with temp_path.open("wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    contract = Contract(file_name=file.filename, owner_id=current_user.id)
    session.add(contract)
    session.commit()
    session.refresh(contract)

    background_tasks.add_task(_process_contract, contract.id, str(temp_path), current_user.id)

    return contract


@router.get("/{contract_id}/status", response_model=ContractStatus)
def get_contract_status(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    contract = session.get(Contract, contract_id)
    if not contract or contract.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Contract not found")

    return ContractStatus(
        id=contract.id, status=contract.status,
        clause_count=contract.clause_count, error_message=contract.error_message,
    )