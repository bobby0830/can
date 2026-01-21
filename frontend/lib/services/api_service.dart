import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/event.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:5000'; // 在實機測試時需改為伺服器 IP

  Future<bool> saveProfile(String username, List<String> interests) async {
    final response = await http.post(
      Uri.parse('$baseUrl/user/profile'),
      headers: {'Content-Type': 'application/json'},
      body: jsonEncode({
        'username': username,
        'interests': interests,
      }),
    );

    return response.statusCode == 200;
  }

  Future<bool> clearCache() async {
    final response = await http.post(Uri.parse('$baseUrl/clear_cache'));
    return response.statusCode == 200;
  }

  Future<List<CalendarEvent>> getRecommendations(String username) async {
    final response = await http.get(
      Uri.parse('$baseUrl/recommendations?username=$username'),
    );

    if (response.statusCode == 200) {
      final Map<String, dynamic> data = jsonDecode(response.body);
      final List<dynamic> eventsJson = data['events'];
      return eventsJson.map((json) => CalendarEvent.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load recommendations');
    }
  }
}










