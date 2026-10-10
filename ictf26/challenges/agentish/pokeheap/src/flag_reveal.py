import os
from langfuse import Langfuse

flag = os.environ.get("FLAG_CHALLENGE", "FLAG_NOT_SET")

langfuse = Langfuse(
    public_key=os.environ.get("LANGFUSE_PUBLIC_KEY", ""),
    secret_key=os.environ.get("LANGFUSE_SECRET_KEY", ""),
    host=os.environ.get("LANGFUSE_HOST", ""),
)

with langfuse.start_as_current_span(name="flag-reveal") as span:
    langfuse.update_current_span(
        input="flag-reveal",
        output=flag,
        metadata={"flag": flag},
    )

langfuse.flush()
print("[flag_reveal] Flag sent to Langfuse.")
