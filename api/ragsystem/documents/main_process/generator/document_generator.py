class DocumentGenerator:
    def __init__(self, template_path):
        self.template = None
        self.set_template(template_path)

    def set_template(self, template_path):
        with open(template_path, "r", encoding="utf-8") as f:
            self.template = f.read()

    def generate_prompt(self, retrieved_chunks):
        content = "\n".join([f"{i + 1}. {chunk}" for i, chunk in enumerate(retrieved_chunks)])
        return self.template.format(content=content)