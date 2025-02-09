from vertexai.preview.vision_models import ImageGenerationModel

generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-001")


def generate_icon(input: str) -> str:
    prompt = f"""
    {input}というキーワードに基づいて、可愛い動物のアイコンを生成してください。
    動物のみを描き、背景は白にしてください。
    人間の要素は一切含めず、純粋な動物の姿で表現してください。
    キーワードは職業に関連するものが多いです。
    その特徴を生かして、動物のアイコンを生成してください。
    繰り返しますが、人間の要素は一切含めず、純粋な動物の姿で表現してください。
    """
    response = generation_model.generate_images(
        prompt=prompt,
        language="ja",
    )
    return response.images[0]._as_base64_string()
