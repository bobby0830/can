import 'package:flutter/material.dart';
import 'package:table_calendar/table_calendar.dart';
import '../services/api_service.dart';
import '../models/event.dart';
import 'package:intl/intl.dart';

class CalendarScreen extends StatefulWidget {
  @override
  _CalendarScreenState createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  final ApiService _apiService = ApiService();
  CalendarFormat _calendarFormat = CalendarFormat.month;
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;
  Map<DateTime, List<CalendarEvent>> _events = {};
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _selectedDay = _focusedDay;
    _fetchEvents();
  }

  Future<void> _fetchEvents() async {
    try {
      final events = await _apiService.getRecommendations('default_user');
      final Map<DateTime, List<CalendarEvent>> eventMap = {};
      
      for (var event in events) {
        try {
          String dateStr = event.date;
          // 處理 2026-01-00 格式，將其視為該月的第一天但標註為待定
          if (dateStr.endsWith("-00")) {
            dateStr = dateStr.replaceAll("-00", "-01");
          }
          
          final date = DateTime.parse(dateStr);
          final day = DateTime(date.year, date.month, date.day);
          if (eventMap[day] == null) eventMap[day] = [];
          eventMap[day]!.add(event);
        } catch (e) {
          print('跳過無效日期格式的事件: ${event.title}, 日期: ${event.date}');
          continue; 
        }
      }

      setState(() {
        _events = eventMap;
        _isLoading = false;
      });
    } catch (e) {
      setState(() => _isLoading = false);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('獲取推薦失敗: $e')));
    }
  }

  List<CalendarEvent> _getEventsForDay(DateTime day) {
    return _events[DateTime(day.year, day.month, day.day)] ?? [];
  }

  void _showEventDetails(CalendarEvent event) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text(event.title),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('推薦理由:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(event.reason),
            SizedBox(height: 10),
            Text('簡介:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(event.description),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: Text('關閉')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('你的個人化科技日曆')),
      body: _isLoading 
        ? Center(child: CircularProgressIndicator())
        : Column(
            children: [
              TableCalendar(
                firstDay: DateTime.utc(2026, 1, 1),
                lastDay: DateTime.utc(2026, 12, 31),
                focusedDay: _focusedDay,
                calendarFormat: _calendarFormat,
                eventLoader: _getEventsForDay,
                selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
                onDaySelected: (selectedDay, focusedDay) {
                  setState(() {
                    _selectedDay = selectedDay;
                    _focusedDay = focusedDay;
                  });
                },
                onFormatChanged: (format) {
                  setState(() {
                    _calendarFormat = format;
                  });
                },
              ),
              const SizedBox(height: 8.0),
              Expanded(
                child: ListView.builder(
                  itemCount: _getEventsForDay(_selectedDay!).length,
                  itemBuilder: (context, index) {
                    final event = _getEventsForDay(_selectedDay!)[index];
                    final bool isTBD = event.date.endsWith("-00");
                    
                    return Card(
                      margin: EdgeInsets.symmetric(horizontal: 12, vertical: 4),
                      child: ListTile(
                        leading: Container(
                          padding: EdgeInsets.all(8),
                          decoration: BoxDecoration(
                            color: isTBD ? Colors.orange.withOpacity(0.2) : Colors.blue.withOpacity(0.2),
                            borderRadius: BorderRadius.circular(8),
                          ),
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Text(
                                isTBD ? "待定" : DateFormat('MM/dd').format(DateTime.parse(event.date)),
                                style: TextStyle(
                                  fontWeight: FontWeight.bold,
                                  color: isTBD ? Colors.orange : Colors.blue,
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                        title: Text(
                          event.title,
                          style: TextStyle(fontWeight: FontWeight.bold),
                        ),
                        subtitle: Text(
                          event.reason,
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                        trailing: Icon(Icons.chevron_right, size: 16),
                        onTap: () => _showEventDetails(event),
                      ),
                    );
                  },
                ),
              ),
            ],
          ),
    );
  }
}










