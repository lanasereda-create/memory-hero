from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

# Ваши данные от Яндекс Облака
FOLDER_ID = "b1gvub7mgvr547lb21l3"
API_KEY = "AQVN0NcLA2EFOkwqtT_rh7GxQk8Ff8ywvx7xp079"

@app.route('/generate', methods=['POST'])
def generate():
    try:
        data = request.json

        # Формируем персонализированный промпт
        system_prompt = (
            "Ты — помощник для сохранения семейной истории. "
            "На основе предоставленных данных о ветеране Великой Отечественной войны "
            "напиши короткий художественный рассказ (2-3 абзаца) о его возможном боевом пути. "
            "Рассказ должен быть уважительным, эмоциональным и подходить для семейного архива. "
            "Обязательно используй дополнительные факты в рассказе, если они предоставлены. "
            "Не используй Markdown-разметку, пиши простым текстом."
        )

        user_message = (
            f"ФИО: {data.get('fio', '')}\n"
            f"Год рождения: {data.get('birthYear', '')}\n"
            f"Место призыва: {data.get('place', '')}\n"
            f"Дополнительные факты: {data.get('extra', 'не указаны')}"
        )

        # Отправляем запрос к YandexGPT
        resp = requests.post(
            "https://llm.api.cloud.yandex.net/foundationModels/v1/completion",
            headers={
                "Authorization": f"Api-Key {API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "modelUri": f"gpt://{FOLDER_ID}/yandexgpt-lite",
                "completionOptions": {
                    "stream": False,
                    "temperature": 0.7,
                    "maxTokens": "600"
                },
                "messages": [
                    {"role": "system", "text": system_prompt},
                    {"role": "user", "text": user_message}
                ]
            }
        )

        result = resp.json()

        if 'result' in result:
            generated_text = result['result']['alternatives'][0]['message']['text']
            return jsonify({"success": True, "story": generated_text})
        else:
            return jsonify({"success": False, "error": str(result)}), 500

    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8090, debug=False)
