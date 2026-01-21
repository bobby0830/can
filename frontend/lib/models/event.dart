class CalendarEvent {
  final String title;
  final String date;
  final String description;
  final String reason;
  final String link;
  final double score;

  CalendarEvent({
    required this.title,
    required this.date,
    required this.description,
    required this.reason,
    required this.link,
    required this.score,
  });

  factory CalendarEvent.fromJson(Map<String, dynamic> json) {
    return CalendarEvent(
      title: json['title'] ?? '',
      date: json['date'] ?? '',
      description: json['description'] ?? '',
      reason: json['reason'] ?? '',
      link: json['link'] ?? '',
      score: (json['score'] ?? 0.0).toDouble(),
    );
  }
}










