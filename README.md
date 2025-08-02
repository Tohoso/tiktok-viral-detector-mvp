# TikTok Viral Video Detector MVP

🚀 **TikAPI-powered viral video detection tool with Google Sheets integration**

Automatically finds TikTok videos that achieve 500k+ views within 24 hours.

## 🆕 **Latest Updates (v1.1)**

### 🔧 **Critical Bug Fixes**
- **Fixed TikAPI JSON parse error** - Resolved authentication header issue
- **Enhanced error handling** - Added Content-Type validation and detailed logging
- **Multiple endpoint support** - Fallback strategy for improved reliability

### ✨ **New Features**
- **Connection diagnostic tool** - `test_tikapi_connection.py` for troubleshooting
- **Enhanced debugging** - Detailed logs with `tikapi_debug.log`
- **Improved authentication** - Correct `X-API-KEY` header implementation

## 📦 **Files Overview**

### **Core Application**
- `main.py` - Original MVP application
- `main_fixed.py` - **🆕 Enhanced version with bug fixes**
- `config.json.template` - Configuration template

### **Testing & Debugging**
- `test_mvp.py` - Comprehensive test suite
- `test_tikapi_connection.py` - **🆕 TikAPI connection diagnostic tool**

### **Documentation**
- `README.md` - This file
- `google_sheets_setup.md` - Google Sheets integration guide

## 🚀 **Quick Start**

### **Option 1: Use Fixed Version (Recommended)**
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Test TikAPI connection
python test_tikapi_connection.py

# 3. Create configuration
python main_fixed.py --create-config

# 4. Edit config.json with your API key

# 5. Run the detector
python main_fixed.py
```

### **Option 2: Use Original Version**
```bash
# Follow the same steps but use main.py instead of main_fixed.py
python main.py --create-config
python main.py
```

## 🔧 **Troubleshooting**

### **JSONDecodeError Issues**

If you encounter:
```
❌ JSONパースエラー: Expecting value: line 1 column 1 (char 0)
```

**Solution:**
1. Use the **fixed version**: `python main_fixed.py`
2. Run diagnostic tool: `python test_tikapi_connection.py`
3. Check the debug log: `cat tikapi_debug.log`

### **Common Issues & Solutions**

| Issue | Solution |
|-------|----------|
| Invalid API Key | Verify key in TikAPI dashboard |
| HTML response instead of JSON | Use `main_fixed.py` with correct headers |
| Connection timeout | Check network and proxy settings |
| Rate limit exceeded | Wait or upgrade TikAPI plan |

## 📊 **Features**

### **Core Functionality**
- ✅ **24-hour viral detection** - Finds videos with 500k+ views in 24h
- ✅ **Multi-region support** - US, Japan, and other countries
- ✅ **Google Sheets export** - Automatic spreadsheet integration
- ✅ **CSV output** - Local file export with comprehensive data

### **Technical Features**
- ✅ **Rate limiting** - Respects API limits
- ✅ **Error handling** - Robust exception management
- ✅ **Logging system** - Detailed debug information
- ✅ **Multiple endpoints** - Fallback strategy for reliability

### **Data Points Collected**
- Video ID, description, view count
- Likes, comments, shares
- Author information and follower count
- Post time and viral speed calculation
- Hashtags and verification status
- Direct video URLs

## 🔑 **API Key Setup**

### **Get TikAPI Key**
1. Visit [TikAPI.io](https://tikapi.io/)
2. Create account and get API key
3. Add key to `config.json`:
```json
{
  "tikapi_key": "your_actual_api_key_here"
}
```

### **Test Your Setup**
```bash
python test_tikapi_connection.py
```

## 📈 **Expected Output**

### **Console Output**
```
🚀 TikTok バイラル動画検出を開始します
📊 条件: 24時間以内に500,000再生以上
🌍 US 地域の動画を検索中...
📈 リクエスト 1/10: 30件処理, 3件バイラル検出
🔥 バイラル動画: Amazing dance trend... (1,500,000再生, 18h経過)
✅ 収集完了: 300件処理, 12件のバイラル動画を検出
📄 CSVファイル: viral_videos_20250802_143022.csv
📊 Google Sheetsに出力完了
```

### **CSV Output Example**
```csv
動画ID,説明,再生数,いいね数,コメント数,シェア数,アカウント名,フォロワー数,投稿日時,経過時間(h),バイラル速度,動画URL,ハッシュタグ,認証済み
7123456789,Amazing dance trend...,1500000,75000,5000,2000,dancer_pro,250000,2025-08-02 10:30:00,18.0,83333,https://www.tiktok.com/@dancer_pro/video/7123456789,viral dance fyp,
```

## 🛠️ **Development**

### **Project Structure**
```
tiktok-viral-detector-mvp/
├── main.py                    # Original application
├── main_fixed.py             # Enhanced version (recommended)
├── test_tikapi_connection.py # Diagnostic tool
├── test_mvp.py              # Test suite
├── config.json.template     # Configuration template
├── requirements.txt         # Dependencies
├── README.md               # Documentation
└── google_sheets_setup.md  # Google Sheets guide
```

### **Key Classes**
- `TikAPIClient` - API communication with enhanced error handling
- `ViralVideoDetector` - Core detection logic
- `GoogleSheetsExporter` - Spreadsheet integration

## 📋 **Requirements**

### **Python Dependencies**
```
requests>=2.31.0
gspread>=5.10.0
google-auth>=2.22.0
google-auth-oauthlib>=1.0.0
google-auth-httplib2>=0.1.0
```

### **External Services**
- [TikAPI](https://tikapi.io/) - TikTok data access
- [Google Sheets API](https://developers.google.com/sheets/api) - Spreadsheet integration (optional)

## 🎯 **Use Cases**

### **Content Creators**
- Discover trending content patterns
- Identify viral video characteristics
- Find inspiration for new content

### **Marketing Teams**
- Track viral marketing campaigns
- Analyze competitor content performance
- Identify influencer opportunities

### **Researchers**
- Study viral content propagation
- Analyze social media trends
- Collect data for academic research

## 🔄 **Version History**

### **v1.1 (Latest)**
- 🔧 Fixed TikAPI authentication issues
- ✨ Added connection diagnostic tool
- 🛠️ Enhanced error handling and logging
- 📊 Improved debugging capabilities

### **v1.0**
- 🚀 Initial MVP release
- ✅ Basic viral video detection
- 📊 Google Sheets integration
- 📄 CSV export functionality

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 **License**

This project is open source. See the repository for license details.

## 🆘 **Support**

### **Issues & Questions**
- Create an issue on GitHub
- Check existing issues for solutions
- Use the diagnostic tool for troubleshooting

### **Feature Requests**
- Submit feature requests via GitHub issues
- Describe your use case and requirements
- Consider contributing the feature yourself

## 🔗 **Links**

- **Repository**: https://github.com/Tohoso/tiktok-viral-detector-mvp
- **TikAPI Documentation**: https://tikapi.io/documentation/
- **Google Sheets API**: https://developers.google.com/sheets/api

---

**Made with ❤️ for the content creator community**

