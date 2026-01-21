import 'package:flutter/material.dart';
import 'screens/survey_screen.dart';

void main() {
  runApp(CalendarSuggestApp());
}

class CalendarSuggestApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Calendar Suggestion System',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        useMaterial3: true,
      ),
      home: SurveyScreen(),
    );
  }
}










