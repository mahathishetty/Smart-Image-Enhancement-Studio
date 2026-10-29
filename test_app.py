import io, unittest
from PIL import Image
import app as webapp

class SmokeTests(unittest.TestCase):
    def setUp(self):
        webapp.app.config["TESTING"]=True
        self.client=webapp.app.test_client()
    def test_home(self):
        r=self.client.get("/")
        self.assertEqual(r.status_code,200)
        self.assertIn(b"ClarityLab",r.data)
    def test_missing_image(self):
        self.assertEqual(self.client.post("/api/enhance",data={}).status_code,400)
    def test_process_png(self):
        buff=io.BytesIO()
        Image.new("RGB",(48,48),(60,80,100)).save(buff,format="PNG");buff.seek(0)
        r=self.client.post("/api/enhance",data={"image":(buff,"test.png"),"method":"auto","strength":"1","gamma":".8","clipLimit":"2"},content_type="multipart/form-data")
        self.assertEqual(r.status_code,200,r.get_data(as_text=True))
        self.assertTrue(r.get_json()["success"])
if __name__=="__main__": unittest.main()
