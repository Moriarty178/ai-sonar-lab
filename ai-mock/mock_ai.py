from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Request(BaseModel):
    model: str
    messages: list

@app.post("/v1/chat/completions")
def chat(req: Request):
    return {
        "choices": [
            {
                "message": {
                    "content": """1. Đây là lỗi bảo mật.
2. Nguyên nhân: xử lý input không an toàn.
3. Fix:
```java
PreparedStatement stmt = connection.prepareStatement("SELECT * FROM users WHERE name = ?");
```"""
                }
            }
        ]
    }