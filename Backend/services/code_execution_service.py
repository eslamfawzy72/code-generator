import subprocess
import tempfile
import time
from pathlib import Path

from schemas.generation_response import CodeGenerationResponse
from schemas.execution_response import ExecutionResponse


class ExecutionService:

    def __init__(self, timeout: int = 5):
        self.timeout = timeout

    def execute(
        self,
        generation: CodeGenerationResponse
    ) -> ExecutionResponse:

        suffix = self._get_file_extension(generation.language)

        with tempfile.TemporaryDirectory() as temp_dir:

            source_file = Path(temp_dir) / f"solution{suffix}"

            source_file.write_text(
                generation.code,
                encoding="utf-8"
            )

            command = self._build_command(
                generation.language,
                source_file
            )

            start = time.perf_counter()

            try:

                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )

                execution_time = (
                    time.perf_counter() - start
                )

                return ExecutionResponse(
                    success=result.returncode == 0,
                    stdout=result.stdout,
                    stderr=result.stderr,
                    exit_code=result.returncode,
                    execution_time=execution_time
                )

            except subprocess.TimeoutExpired:

                execution_time = (
                    time.perf_counter() - start
                )

                return ExecutionResponse(
                    success=False,
                    stdout="",
                    stderr=f"Execution exceeded {self.timeout} seconds.",
                    exit_code=-1,
                    execution_time=execution_time
                )

    def _get_file_extension(
        self,
        language: str
    ) -> str:

        mapping = {
            "python": ".py",
        }

        return mapping[language]

    def _build_command(
        self,
        language: str,
        source_file: Path
    ) -> list[str]:

        if language == "python":
            return ["python", str(source_file)]

        raise ValueError(
            f"Unsupported language: {language}"
        )