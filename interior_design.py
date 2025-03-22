from delphifmx import *
import requests
import base64
import io

# Replace with your API keys
REPLICATE_API_TOKEN = "r8_91TNmim5tRoF5UPb65gHFdRDQchcM131DJleF"
IMGBB_API_KEY = "https://i.ibb.co/Dfbtf4bw/aiinterior-design.png"

class InteriorDesignApp(Form):

    def __init__(self, owner):
        self.Caption = "AI Interior Design - Powered by Replicate"
        self.SetBounds(100, 100, 800, 600)

        # Upload Button
        self.UploadButton = Button(self)
        self.UploadButton.Parent = self
        self.UploadButton.Text = "Upload Room Image"
        self.UploadButton.SetBounds(30, 30, 200, 40)
        self.UploadButton.OnClick = self.on_upload_click

        # Generate Button
        self.GenerateButton = Button(self)
        self.GenerateButton.Parent = self
        self.GenerateButton.Text = "Generate AI Design"
        self.GenerateButton.SetBounds(250, 30, 200, 40)
        self.GenerateButton.OnClick = self.on_generate_click

        # Image Views
        self.OriginalImage = Image(self)
        self.OriginalImage.Parent = self
        self.OriginalImage.SetBounds(30, 90, 320, 320)

        self.AIImage = Image(self)
        self.AIImage.Parent = self
        self.AIImage.SetBounds(400, 90, 320, 320)

        # Status Label
        self.StatusLabel = Label(self)
        self.StatusLabel.Parent = self
        self.StatusLabel.Text = ""
        self.StatusLabel.SetBounds(30, 430, 700, 40)

        self.local_image_path = None
        self.image_url = None

    def on_upload_click(self, sender):
        dlg = OpenDialog(self)
        dlg.Title = "Select an Image"
        if dlg.Execute():
            self.local_image_path = dlg.FileName
            self.OriginalImage.Bitmap.LoadFromFile(self.local_image_path)
            self.StatusLabel.Text = "Image loaded. Ready to send."

    def on_generate_click(self, sender):
        if not self.local_image_path:
            self.StatusLabel.Text = "Please upload an image first!"
            return

        self.StatusLabel.Text = "Uploading to imgbb..."
        self.image_url = self.upload_image_to_imgbb(self.local_image_path)

        if not self.image_url:
            self.StatusLabel.Text = "Image upload failed."
            return

        self.StatusLabel.Text = "Calling Replicate API..."
        ai_image_url = self.send_to_replicate(self.image_url)

        if ai_image_url:
            self.StatusLabel.Text = "AI design generated!"
            self.load_image_from_url(ai_image_url, self.AIImage)
        else:
            self.StatusLabel.Text = "Replicate API failed."

    def upload_image_to_imgbb(self, file_path):
        with open(file_path, "rb") as f:
            b64 = base64.b64encode(f.read())
        url = "https://api.imgbb.com/1/upload"
        payload = {
            "key": IMGBB_API_KEY,
            "image": b64
        }
        response = requests.post(url, data=payload)
        if response.status_code == 200:
            return response.json()["data"]["url"]
        return None

    def send_to_replicate(self, image_url):
        url = "https://api.replicate.com/v1/predictions"
        headers = {
            "Authorization": f"Token {REPLICATE_API_TOKEN}",
            "Content-Type": "application/json"
        }

        payload = {
            "version": "dc2ce5a9753580b2c246b778dcceddf5",  # Replace with correct model version
            "input": {
                "image": image_url
            }
        }

        response = requests.post(url, json=payload, headers=headers)
        if response.status_code != 201:
            return None

        prediction_url = response.json()["urls"]["get"]

        # Poll the result
        while True:
            res = requests.get(prediction_url, headers=headers)
            output = res.json()
            if output["status"] == "succeeded":
                return output["output"]
            elif output["status"] == "failed":
                return None

    def load_image_from_url(self, url, image_control):
        response = requests.get(url)
        if response.status_code == 200:
            image_stream = io.BytesIO(response.content)
            image_control.Bitmap.LoadFromStream(image_stream)

def main():
    Application.Initialize()
    Application.Title = "AI Interior Design App"
    Application.MainForm = InteriorDesignApp(Application)
    Application.Run()

if __name__ == '__main__':
    main()
