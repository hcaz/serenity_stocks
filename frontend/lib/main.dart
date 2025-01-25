import 'dart:async';
import 'dart:js';
import 'package:flutter/material.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  // This widget is the root of your application.
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Serenity Stocks',
      home: const MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  String _timeString = '';

  late Timer _timer;

  @override
  void initState() {
    _timer = Timer.periodic(Duration(seconds: 1), (Timer t) => _getTime());
    super.initState();

    _getTime();

    context.callMethod('clippyInit');
    context.callMethod('clippySpeak', ['Hello from Dart!']);
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  void _getTime() {
    final DateTime now = DateTime.now();
    final String formattedDateTime = now.hour.toString().padLeft(2, '0') + ':' + now.minute.toString().padLeft(2, '0') + ':' + now.second.toString().padLeft(2, '0');
    setState(() {
      _timeString = formattedDateTime;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        width: double.infinity,
        height: double.infinity,
        decoration: BoxDecoration(
          image: DecorationImage(image: AssetImage('background.jpeg'), fit: BoxFit.cover)
        ),
      ),
      bottomNavigationBar: Container(
        decoration: BoxDecoration(
            gradient: LinearGradient(colors: [Color(0xFF245DDA), Color(0xFF0D47DB)], begin: Alignment.bottomCenter, end: Alignment.topCenter),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.5),
              spreadRadius: 5,
              blurRadius: 7,
              offset: Offset(0, 3), // changes position of shadow
            ),
          ],
        ),
        height: 40,
        child: Row(children: [
          Container(
            width: 150,
            height: double.infinity,
            decoration: BoxDecoration(
              gradient: LinearGradient(colors: [Color(0xFF23AF4E), Color(0xFF1D8A3D)], begin: Alignment.bottomCenter, end: Alignment.topCenter),
            ),
            child: Row(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(Icons.window_sharp, color: Colors.white),
                SizedBox(width: 5),
                Text('stonks', style: TextStyle(color: Colors.white, fontSize: 20, fontStyle: FontStyle.italic)),
              ],
            ),
          ),
          Spacer(),
          Text(_timeString, style: TextStyle(color: Colors.white, fontSize: 20)),
          SizedBox(width: 10),
        ],),
      ),
    );
  }
}
