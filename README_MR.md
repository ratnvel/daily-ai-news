# Free Auto News System — सुरुवातीचा प्रोटोटाइप

हा प्रोजेक्ट Google News RSS फीडमधून AI/Technology/Business विषयांचे headlines आणि लहान descriptions गोळा करून रोजचा Markdown digest तयार करतो. तो **स्वतः AI ने तथ्ये पडताळत नाही** आणि सुरुवातीला WordPress वर आपोआप प्रकाशित करत नाही.

## Windows वर चालवणे

1. Python 3.12 किंवा त्यापुढील आवृत्ती स्थापित असू द्या.
2. या फोल्डरमध्ये Command Prompt उघडा.
3. चालवा:

   ```bat
   python -m pip install -r requirements.txt
   python app.py
   ```

4. तयार झालेला लेख `output` फोल्डरमध्ये दिसेल.

## पूर्ण ऑटोमेशनबद्दल

- `.github/workflows/daily-news.yml` GitHub Actions वर रोज सकाळी साधारण 7:00 IST ला चालण्यासाठी आहे. GitHub repository मध्ये हा प्रोजेक्ट ठेवून Actions सक्षम करावे लागेल.
- GitHub Actions वेळापत्रक विलंबाने चालू शकते; याला हमखास मिनिट-पर-मिनिट वेळ समजू नका.
- WordPress REST API ने पोस्ट पाठवण्याची सोय कोडमध्ये आहे. पण वेबसाइट, WordPress username आणि Application Password तुम्हालाच तुमच्या खात्यात तयार करून सुरक्षित GitHub Secrets मध्ये ठेवावे लागतील.
- प्रथम `AUTO_PUBLISH=false` ठेवा; पोस्ट draft म्हणून तपासा. पूर्ण विश्वास बसल्यावरच स्वतःच्या निर्णयाने publishing सक्षम करा.
- Google AdSense मंजुरी, वेबसाइट ट्रॅफिक किंवा उत्पन्नाची हमी नाही. मोफत hosting वर मर्यादा असू शकतात.

## महत्त्वाच्या मर्यादा

- हा RSS digest आहे, पूर्ण AI पत्रकार नाही.
- RSS मधील बातम्या चुकीच्या/अपूर्ण असू शकतात. महत्त्वाच्या दाव्यांची दुसऱ्या विश्वसनीय स्रोतांतून पडताळणी करा.
- इतर वेबसाइटचे संपूर्ण लेख किंवा फोटो कॉपी करू नका. मूळ स्रोताची लिंक आणि श्रेय द्या; स्वतःचे विश्लेषण जोडा.
- फक्त मोठ्या प्रमाणात AI मजकूर प्रकाशित केल्याने Google Search ranking किंवा AdSense मंजुरी मिळत नाही.
- Password/API secrets कधीही सार्वजनिक repository मध्ये टाकू नका.
