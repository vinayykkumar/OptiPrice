
# 🛠 OptiPrice Prognasticator


OptiPrice Prognosticator is a dynamic pricing prediction platform tailored for the oil and gas industry, enabling smart revenue optimization and real-time insights.

✔ Predict optimal selling prices using ML models 📈

✔ Analyze trends from 150K+ historical sales records 🧾

✔ Query customer-specific prices from a secure database 🔐

✔ Automate updates using XGBoost + LSTM for time series ⚙️

Built with Python, SQL, Streamlit UI, and scalable ML models, OptiPrice Prognosticator helps businesses stay competitive in fluctuating markets.


---

---

🚀 Features

✅ Dynamic Price Prediction – Uses ML models (XGBoost , LSTM) through transfer Learning.

✅ Time Series & Trend Analysis – Leverages 150K+ historical sales data for accurate insights.

✅ Python Visualization – Visualize past 20-day pricing trends and customer discounts.

✅ Real-Time Query System – Fetch selling prices based on customer-specific order data.

✅ Integrated Database Support – Stores customer orders, prices, and discount history securely.

✅ Deployment-Ready – Scalable across cloud platforms (Azure, AWS) or local infrastructure.





## 🛠 Tech Stack 
  

---

**📌 Programming Language**  
- 🐍 **Python 3.8+** – For data preprocessing, model training, and backend automation.  

---


---

**📂 Database & Data Storage**  
- 🛢️ **PostgreSQL / MySQL** – Stores historical oil & gas price data and external features.  
- 📄 **CSV / Excel Files** - Used for bulk loading/exporting time-series data and model outputs.


---

---

**🌐 Data Collection & APIs**  
- 🌎 **EIA / Quandl APIs** – Fetches real-time oil & gas price, demand, and supply metrics. 
- 🔍 **Web Scraping (BeautifulSoup)** – Extracts additional data from news, indices, and portals.
- 📡 **Requests** – Automates data retrieval and updates.

---

---
### **⚡ Performance Optimization**  
- ⚡ **XGBoost & Transfer-Learned LSTM** – Combines structured modeling and deep temporal learning for high accuracy (99%).  
- 🧠 **Transfer Learning** – Speeds up LSTM training using pre-trained time series patterns. 
- 🧮 **Batch Predictions** – Handles large-scale forecasting across multiple regions.

---

---

### **📦 Libraries & Dependencies**  
| 📦 **Library**  | 📝 **Usage**  |  
|---------------|--------------|  
| `xgboost` | Structured data modeling and prediction |  
| `tensorflow/keras` | LSTM-based time series forecasting |  
| `pandas` | Data handling and transformation |  
| `scikit-learn` | Evaluation metrics, scaling, feature engineering |  
| `beautifulsoup4` | Scraping external price and news data |  
| `matplotlib` | Graphing price trends and model results |  

---

 

---

### **🔐 Security & Best Practices**  
- 🔑 **Environment Variables** – For API keys, DB credentials, and deployment secrets.  
- 🚫 **`.gitignore`** – Prevents leaking sensitive configs and model weights.  

---




## Deployment

💻 Installation & Setup

🔹 Prerequisites

Before running the project, install the following:

✅ Python 3.8+ – Install from Python.org

✅ Streamlit – For interactive UI

✅ Pip & Virtual Environment



1. **Clone the repository**



```bash
git clone https://github.com/roshankraveendrababu/Optiprice-Prognasticator.git
cd Optiprice-Prognasticator
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Launch the Streamlit App**
```bash
streamlit run app.py

```






## Screenshots

![User Interface](https://github.com/user-attachments/assets/c7d32017-787a-4315-bd22-4b8e340b062e)



## 🛠 Contributions

Contributions are always welcome!


👨‍💻 How to Contribute

1. Fork the repo 🍴

2. Create a new branch (feature-branch)

3. Commit your changes

4. Submit a pull request


## 🙏 Acknowledgments

We would like to express our gratitude to:

1. Mr.Vinay Kumar (Mentor) –  I sincerely thank you for providing step-by-step guidance and invaluable insights throughout the project.

2. Yahoo Finance & Public Oil Price APIs – For providing open access to historical and real-time oil and gas pricing data.

3. Open-Source Contributors & Python Community – For maintaining essential libraries like **pandas**, **xgboost**, **lightgbm**, and **streamlit**, which powered the data processing and visualization


## Authors

- [@Roshan.K.R](https://github.com/roshankraveendrababu)

- [@Sanika Mulik](https://github.com/sanikamulik)

## 🔗 Links

[![linkedin](https://img.shields.io/badge/linkedin-0A66C2?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/roshan-konidhala/)

[![twitter](https://img.shields.io/badge/twitter-1DA1F2?style=for-the-badge&logo=twitter&logoColor=white)](https://x.com/RoshanKR0912)


