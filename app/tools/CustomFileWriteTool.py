import os
from typing import Optional, Dict, Any, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field, model_validator
from i18n import t

class FixedCustomFileWriteToolInputSchema(BaseModel):
    content: str = Field(..., description=t('tool.file_content'))
    mode: str = Field(..., description=t('tool.file_mode'))

class CustomFileWriteToolInputSchema(FixedCustomFileWriteToolInputSchema):
    content: str = Field(..., description=t('tool.file_content'))
    mode: str = Field(..., description=t('tool.file_mode'))
    filename: str = Field(..., description=t('tool.filename'))

class CustomFileWriteTool(BaseTool):
    name: str = t('tool.file_write')
    description: str = t('tool.file_write_desc')
    args_schema: Type[BaseModel] = CustomFileWriteToolInputSchema
    filename: Optional[str] = None

    def __init__(self, base_folder: str, filename: Optional[str] = None, **kwargs):
        super().__init__(**kwargs)
        if filename is not None and len(filename) > 0:
            self.args_schema = FixedCustomFileWriteToolInputSchema
        self._base_folder = base_folder
        self.filename = filename or None
        self._ensure_base_folder_exists()
        self._generate_description()


    def _ensure_base_folder_exists(self):
        os.makedirs(self._base_folder, exist_ok=True)

    def _get_full_path(self, filename: Optional[str]) -> str:
        if filename is None and self.filename is None:
            raise ValueError("No filename specified and no default file set.")

        chosen_file = filename or self.filename
        full_path = os.path.abspath(os.path.join(self._base_folder, chosen_file))

        if not full_path.startswith(os.path.abspath(self._base_folder)):
            raise ValueError(t('tool.access_denied'))  #TODO: add validations for path traversal

        return full_path

    def _run(self, content: str, mode: str, filename: Optional[str] = None) -> Dict[str, Any]:
        full_path = self._get_full_path(filename)
        try:
            with open(full_path, 'a' if mode == 'a' else 'w') as file:
                file.write(content)
            if mode == 'a':
                message = t('tool.success_appended', path=full_path)
            else:
                message = t('tool.success_written', path=full_path)
            return {
                "status": t('tool.success_status'),
                "message": message
            }
        except Exception as e:
            return {
                "status": t('tool.error_status'),
                "message": str(e)
            }

    def run(self, input_data: CustomFileWriteToolInputSchema) -> Any:
        response_data = self._run(
            content=input_data.content,
            mode=input_data.mode,
            filename=input_data.filename
        )
        return response_data
