import boto3

bedrock = boto3.client(
    service_name="bedrock-runtime",
    region_name="us-east-1"
)

def invoke_llm(prompt: str):
    response = bedrock.invoke_model(
        modelId="anthropic.claude-v2",
        body=f'{{"prompt": "{prompt}", "max_tokens_to_sample": 300}}'
    )

    return response["body"].read().decode()