import 'package:flutter/material.dart';
import '../services/api_service.dart';
import 'calendar_screen.dart';

class SurveyScreen extends StatefulWidget {
  @override
  _SurveyScreenState createState() => _SurveyScreenState();
}

class _SurveyScreenState extends State<SurveyScreen> {
  final ApiService _apiService = ApiService();
  final List<String> _topics = [
    'AI',
    '機器學習',
    '前端開發',
    '後端開發',
    '雲端運算',
    '區塊鏈',
    '網路安全',
    '物聯網',
    '美國金融',
    '美國政治'
  ];
  final List<String> _selectedTopics = [];
  final TextEditingController _customKeywordController = TextEditingController();

  void _toggleTopic(String topic) {
    setState(() {
      if (_selectedTopics.contains(topic)) {
        _selectedTopics.remove(topic);
      } else {
        _selectedTopics.add(topic);
      }
    });
  }

  Future<void> _submit() async {
    final allSelected = List<String>.from(_selectedTopics);
    if (_customKeywordController.text.trim().isNotEmpty) {
      allSelected.add(_customKeywordController.text.trim());
    }

    if (allSelected.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('請至少選擇一個興趣主題或輸入關鍵字')));
      return;
    }

    bool success = await _apiService.saveProfile('default_user', allSelected);
    if (success) {
      Navigator.pushReplacement(
        context,
        MaterialPageRoute(builder: (context) => CalendarScreen()),
      );
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('儲存失敗，請檢查後端連線')));
    }
  }

  Future<void> _clearCache() async {
    bool success = await _apiService.clearCache();
    if (success) {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('快取已清空')));
    } else {
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('清空快取失敗')));
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('自定義你的個人日曆'),
        actions: [
          IconButton(
            icon: Icon(Icons.delete_sweep),
            tooltip: '清空事件快取',
            onPressed: () {
              showDialog(
                context: context,
                builder: (context) => AlertDialog(
                  title: Text('清空快取'),
                  content: Text('這將刪除所有已存儲的日曆事件，下次搜尋將重新爬取。確定嗎？'),
                  actions: [
                    TextButton(onPressed: () => Navigator.pop(context), child: Text('取消')),
                    TextButton(
                      onPressed: () {
                        Navigator.pop(context);
                        _clearCache();
                      },
                      child: Text('確定', style: TextStyle(color: Colors.red)),
                    ),
                  ],
                ),
              );
            },
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('選擇你感興趣的主題：', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 15),
            Wrap(
              spacing: 10,
              runSpacing: 10,
              children: _topics.map((topic) {
                final isSelected = _selectedTopics.contains(topic);
                return FilterChip(
                  label: Text(topic),
                  selected: isSelected,
                  onSelected: (_) => _toggleTopic(topic),
                  selectedColor: Colors.blue.shade200,
                );
              }).toList(),
            ),
            SizedBox(height: 30),
            Text('或輸入自定義關鍵字：', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
            SizedBox(height: 15),
            TextField(
              controller: _customKeywordController,
              decoration: InputDecoration(
                hintText: '例如: Tesla Earnings, Space SpaceX, NBA...',
                border: OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: Icon(Icons.clear),
                  onPressed: () => _customKeywordController.clear(),
                ),
              ),
            ),
            SizedBox(height: 40),
            Center(
              child: ElevatedButton(
                onPressed: _submit,
                child: Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 40, vertical: 15),
                  child: Text('生成個人日曆', style: TextStyle(fontSize: 18)),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}










