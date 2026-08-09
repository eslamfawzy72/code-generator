from services.code_execution_service import ExecutionService

from schemas.generation_response import CodeGenerationResponse
from dto.intents  import Intent


executor = ExecutionService()



response = CodeGenerationResponse(
    intent=Intent.GENERATE ,
    language="python",

    code="""

print("Hello World")



for i in range(5):

    print(i)

"""

)



result = executor.execute(response)



print(result)