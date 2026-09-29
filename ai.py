from flask import Flask, request, jsonify
import boto3

app = Flask(__name__)

# Connect to Floci Bedrock Runtime
import os

client = boto3.client(
    "bedrock-runtime",
    region_name="ap-south-1",
    endpoint_url=os.getenv(
        "BEDROCK_ENDPOINT_URL",
        "http://localhost:4566"
    )
)

model_id = "global.amazon.nova-2-lite-v1:0"

# Load operations runbook
with open("runbooks/deployment-troubleshooting.txt", "r") as file:
    runbook = file.read()


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"status": "Healthy"}), 200


@app.route("/invocations", methods=["POST"])
def invocations():
    data = request.get_json(silent=True) or {}

    question = data.get("prompt")

    if not question:
        question = data.get("input", {}).get("prompt")

    if not question:
        return jsonify({
            "error": "No prompt provided"
        }), 400

    prompt = f"""
You are an AI Operations Assistant.

Answer the user's question using only the information
provided in the operations runbook.

If the answer is not present in the runbook, say that
the information is not available in the runbook.

Operations Runbook:
{runbook}

User Question:
{question}
"""

    try:
        response = client.converse(
            modelId=model_id,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"text": prompt}
                    ]
                }
            ]
        )

        answer = response["output"]["message"]["content"][0]["text"]

        return jsonify({
            "result": answer
        }), 200

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8080
    )