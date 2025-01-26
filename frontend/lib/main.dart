import 'dart:async';
import 'dart:convert';
import 'dart:js';
import 'package:chart_sparkline/chart_sparkline.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:flutter_chess_board/flutter_chess_board.dart' as chess;
import 'package:flutter_floaty/flutter_floaty.dart';
import 'package:gpt_markdown/gpt_markdown.dart';
import 'package:http/http.dart' as http;
import 'package:indexed/indexed.dart';

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
      debugShowCheckedModeBanner: false,
    );
  }
}

class MyHomePage extends StatefulWidget {
  const MyHomePage({super.key});

  @override
  State<MyHomePage> createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  final _apiEndpoint = 'http://127.0.0.1:8000';
  String _timeString = '';

  late Timer _timer;

  bool _clippyInit = false,
      _windowLogin = true,
      _windowMail = false,
      _windowStocks = false,
      _windowNews = false,
      _windowChess = false;

  List<String> _windowOrder = ['news', 'chess', 'mail', 'stock'];

  final TextEditingController _screenNameController =
      TextEditingController(text: 'zach@example.com');
  final FocusNode _screenNameFocusNode = FocusNode();
  chess.ChessBoardController controller = chess.ChessBoardController();

  JsObject clippytContext = context;

  Map<String, dynamic>? _userData, _currentMessage, _currentStock, _currentNews;
  List<dynamic>? _notifications, _stocks, _news;

  @override
  void initState() {
    _timer = Timer.periodic(Duration(seconds: 1), (Timer t) => _getTime());
    super.initState();

    _getTime();
  }

  @override
  void dispose() {
    _timer.cancel();
    super.dispose();
  }

  void _getTime() {
    final DateTime now = DateTime.now();
    final String formattedDateTime =
        '${now.hour.toString().padLeft(2, '0')}:${now.minute.toString().padLeft(2, '0')}:${now.second.toString().padLeft(2, '0')}';
    setState(() {
      _timeString = formattedDateTime;
    });

    if (now.second % 20 == 0) {
      if(_windowMail) _getMail();
      if(_windowMail) _getNews();
      if(_windowStocks) _getStocks();
    }
  }

  void _login() async {
    if (!_clippyInit) {
      clippytContext.callMethod('clippyInit');
      _clippyInit = true;
    }

    if (_screenNameController.text.isEmpty) {
      clippytContext.callMethod('clippySpeak', [
        'Im sorry, but you must enter a screen name to sign on to Serenity Stocks!'
      ]);
      _screenNameFocusNode.requestFocus();
      return;
    }
    if (!_screenNameController.text.contains('@')) {
      _screenNameController.text =
          _screenNameController.text + '@serenitystocks.com';
    }
    clippytContext.callMethod('clippySpeak', ['Logging in...']);

    setState(() {
      _windowLogin = false;
      _windowChess = true;
    });

    try {
      // Do a get request
      http.Response response = await http
          .get(Uri.parse('$_apiEndpoint/login/${_screenNameController.text}'));
      if (response.statusCode == 200) {
        _userData = jsonDecode(response.body);
        clippytContext.callMethod('clippySpeak',
            ['You have successfully signed on to Serenity Stocks!']);

        _getMail();
        _getStocks();
        _getNews();
      } else {
        throw Exception('Error signing on');
      }
    } catch (e, s) {
      clippytContext.callMethod('clippySpeak', [
        'There was an error signing on to Serenity Stocks! Please try again.'
      ]);

      print(e);
      print(s);

      setState(() {
        _windowMail = false;
        _windowLogin = true;
      });
    }
  }

  void _getMail() async {
    setState(() {
      _windowMail = true;
      _notifications = null;
    });

    try {
      // Do a get request
      http.Response response = await http.get(Uri.parse(
          '$_apiEndpoint/notifications/${_screenNameController.text}'));
      if (response.statusCode == 200) {
        List<dynamic> _tmpNotifications = jsonDecode(response.body);

        if (_tmpNotifications.length != _notifications?.length) {
          clippytContext.callMethod('clippySpeak', ['You have new mail!']);
        }

        setState(() {
          _notifications = _tmpNotifications.reversed.toList();
        });
      } else {
        throw Exception('Error getting mail');
      }
    } catch (e, s) {
      clippytContext.callMethod('clippySpeak',
          ['There was an error getting your mail! Please try again.']);

      print(e);
      print(s);

      setState(() {
        _windowLogin = true;
      });
    }
  }
  void _getStocks() async {
    setState(() {
      _windowStocks = true;
    });

    try {
      // Do a get request
      http.Response response = await http.get(Uri.parse(
          '$_apiEndpoint/stocks'));
      if (response.statusCode == 200) {
        List<dynamic> _tmpStocks = jsonDecode(response.body);

        _tmpStocks.forEach((element) {
          List<dynamic> _priceHistory = element['historic_data'] ?? [];

          _priceHistory.sort((a, b) => a['date'].compareTo(b['date']));

          int _limit = 260;
          if(_priceHistory.length > _limit) {
            _priceHistory = _priceHistory.sublist(_priceHistory.length - _limit);
          }

          List<double> _data = [];
          for(int i = 0; i < _priceHistory.length; i++) {
            _data.add(_priceHistory[i]['price'] / 100);
          }

          element['history_data'] = _data;
          element['current_price'] = _priceHistory.last['price'] / 100;
          element['direction'] = _priceHistory.last['price'] > _priceHistory[_priceHistory.length - 2]['price'] ? 'up' : 'down';
          element['historic_data'] = null;
        });

        setState(() {
          _stocks = _tmpStocks;
        });
      } else {
        throw Exception('Error getting stocks');
      }
    } catch (e, s) {
      clippytContext.callMethod('clippySpeak',
          ['There was an error getting your stocks! Please try again.']);

      print(e);
      print(s);

      setState(() {
        _windowLogin = true;
      });
    }
  }
  void _getNews() async {
    setState(() {
      _windowNews = true;
      _news = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Banner(
      message: 'UNREGISTERED HYPERCAM 2',
      location: BannerLocation.topEnd,
      child: Scaffold(
        body: Container(
          width: double.infinity,
          height: double.infinity,
          decoration: BoxDecoration(
              image: DecorationImage(
                  image: AssetImage('background.jpeg'), fit: BoxFit.cover)),
          child: Indexer(children: [
            Indexed(
              index: 9,
              child: FlutterFloaty(
                isVisible: _windowLogin,
                intrinsicBoundaries: Rect.fromLTWH(
                  0,
                  0,
                  MediaQuery.of(context).size.width,
                  MediaQuery.of(context).size.height,
                ),
                enableAnimation: false,
                height: 520,
                width: 350,
                initialX: (MediaQuery.of(context).size.width / 2) - 175,
                initialY: (MediaQuery.of(context).size.height / 2) - 260,
                builder: (context) => Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      Container(
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                              colors: [Color(0xFF245DDA), Color(0xFF0D47DB)],
                              begin: Alignment.bottomCenter,
                              end: Alignment.topCenter),
                        ),
                        child: Row(
                          children: [
                            SizedBox(width: 5),
                            Icon(Icons.directions_run, color: Colors.yellow),
                            SizedBox(width: 5),
                            Text('Sign On',
                                style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 20,
                                    fontStyle: FontStyle.italic)),
                            Spacer(),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.red,
                                borderRadius: BorderRadius.circular(5),
                                border:
                                    Border.all(color: Colors.white, width: 1),
                              ),
                              child: Icon(Icons.close, color: Colors.white),
                            ),
                            SizedBox(width: 5),
                          ],
                        ),
                      ),
                      Padding(
                        padding: EdgeInsets.all(10),
                        child: Column(
                          children: [
                            Container(
                                height: 200,
                                width: 330,
                                decoration: BoxDecoration(
                                  color: Colors.blue[900],
                                ),
                                child: Column(
                                  mainAxisAlignment: MainAxisAlignment.center,
                                  mainAxisSize: MainAxisSize.max,
                                  crossAxisAlignment: CrossAxisAlignment.center,
                                  children: [
                                    Row(
                                      children: [
                                        Spacer(),
                                        Stack(
                                          children: [
                                            Icon(Icons.directions_run,
                                                color: Colors.black, size: 135),
                                            Icon(Icons.directions_run,
                                                color: Colors.yellow,
                                                size: 130),
                                          ],
                                        ),
                                      ],
                                    ),
                                    Text('E-Mail Sign On',
                                        style: TextStyle(
                                            color: Colors.white, fontSize: 30)),
                                  ],
                                )),
                            Divider(color: Colors.black),
                            Row(
                              children: [
                                Text('ScreenName:',
                                    style: TextStyle(
                                        color: Colors.blue[900],
                                        fontWeight: FontWeight.bold,
                                        fontSize: 20)),
                                SizedBox(width: 10),
                                Icon(Icons.key, color: Colors.red),
                              ],
                            ),
                            TextFormField(
                              decoration: const InputDecoration(
                                hintText: '@serenitystocks.com',
                                fillColor: Colors.white,
                                border: OutlineInputBorder(),
                              ),
                              controller: _screenNameController,
                              focusNode: _screenNameFocusNode,
                            ),
                            Text('Password:',
                                style: TextStyle(
                                    color: Colors.blue[900],
                                    fontWeight: FontWeight.bold,
                                    fontSize: 20)),
                            GestureDetector(
                              onTap: _login,
                              child: TextFormField(
                                initialValue: '******',
                                enabled: false,
                                decoration: const InputDecoration(
                                  fillColor: Colors.white,
                                  border: OutlineInputBorder(),
                                ),
                              ),
                            ),
                            SizedBox(height: 10),
                            Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 10),
                              child: Row(
                                children: [
                                  Icon(Icons.help_outline,
                                      color: Colors.grey[300]),
                                  SizedBox(width: 5),
                                  Icon(Icons.settings, color: Colors.grey[300]),
                                  Spacer(),
                                  GestureDetector(
                                    onTap: _login,
                                    child: Column(
                                      children: [
                                        Icon(Icons.directions_walk,
                                            color: Colors.green, size: 30),
                                        Text('Sign On',
                                            style: TextStyle(
                                                fontSize: 13,
                                                fontWeight: FontWeight.bold)),
                                      ],
                                    ),
                                  )
                                ],
                              ),
                            ),
                            SizedBox(height: 10),
                            Text('Version: 6.9.420',
                                style: TextStyle(
                                    color: Colors.grey[300], fontSize: 10)),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                shadow: BoxShadow(
                  color: Colors.black.withOpacity(0.5),
                  spreadRadius: 5,
                  blurRadius: 7,
                  offset: Offset(0, 3), // changes position of shadow
                ),
                backgroundColor: Colors.grey[50]!,
                onDragBackgroundColor: Colors.grey[200]!,
              ),
            ),
            Indexed(
              index: _windowOrder.indexOf('mail'),
              child: FlutterFloaty(
                isVisible: _windowMail,
                intrinsicBoundaries: Rect.fromLTWH(
                  0,
                  0,
                  MediaQuery.of(context).size.width,
                  MediaQuery.of(context).size.height,
                ),
                enableAnimation: false,
                height: 900,
                width: 1200,
                initialX: (MediaQuery.of(context).size.width / 2) - 600,
                initialY: (MediaQuery.of(context).size.height / 2) - 450,
                onTap: () {
                  setState(() {
                    _windowOrder.remove('mail');
                    _windowOrder.add('mail');
                  });
                },
                builder: (context) => Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      Container(
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                              colors: [Color(0xFF245DDA), Color(0xFF0D47DB)],
                              begin: Alignment.bottomCenter,
                              end: Alignment.topCenter),
                        ),
                        child: Row(
                          children: [
                            SizedBox(width: 5),
                            Icon(Icons.mail, color: Colors.yellow),
                            SizedBox(width: 5),
                            Text('E-Mail',
                                style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 20,
                                    fontStyle: FontStyle.italic)),
                            Spacer(),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.red,
                                borderRadius: BorderRadius.circular(5),
                                border:
                                    Border.all(color: Colors.white, width: 1),
                              ),
                              child: Icon(Icons.close, color: Colors.white),
                            ),
                            SizedBox(width: 5),
                          ],
                        ),
                      ),
                      Row(
                        children: [
                          Container(
                            decoration: BoxDecoration(
                              border: Border(
                                  right: BorderSide(color: Colors.black)),
                            ),
                            width: 200,
                            height: 860,
                            child: SingleChildScrollView(
                              child: Column(
                                children: [
                                  Row(
                                    mainAxisAlignment:
                                        MainAxisAlignment.spaceEvenly,
                                    children: [
                                      GestureDetector(
                                        onTap: _getMail,
                                        child: Container(
                                          width: 95,
                                          decoration: BoxDecoration(
                                            color: Colors.green[900],
                                          ),
                                          child: Column(
                                            mainAxisAlignment:
                                                MainAxisAlignment.center,
                                            mainAxisSize: MainAxisSize.max,
                                            crossAxisAlignment:
                                                CrossAxisAlignment.center,
                                            children: [
                                              Icon(Icons.refresh,
                                                  color: Colors.white),
                                              Text('Fetch Mail',
                                                  style: TextStyle(
                                                      color: Colors.white,
                                                      fontSize: 16)),
                                            ],
                                          ),
                                        ),
                                      ),
                                      GestureDetector(
                                        onTap: _getMail,
                                        child: Container(
                                          width: 95,
                                          decoration: BoxDecoration(
                                            color: Colors.blue[900],
                                          ),
                                          child: Column(
                                            mainAxisAlignment:
                                                MainAxisAlignment.center,
                                            mainAxisSize: MainAxisSize.max,
                                            crossAxisAlignment:
                                                CrossAxisAlignment.center,
                                            children: [
                                              Icon(Icons.mail,
                                                  color: Colors.white),
                                              Text('New Mail',
                                                  style: TextStyle(
                                                      color: Colors.white,
                                                      fontSize: 16)),
                                            ],
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                  Visibility(
                                    visible: _notifications != null,
                                    replacement: Padding(
                                      padding: const EdgeInsets.all(15.0),
                                      child: CircularProgressIndicator(),
                                    ),
                                    child: ListView.builder(
                                      shrinkWrap: true,
                                      itemCount: _notifications?.length ?? 0,
                                      itemBuilder: (context, index) {
                                        return ListTile(
                                          leading: Icon(Icons.mail,
                                              color: _notifications?[index]
                                                          ['read_by_user'] ==
                                                      true
                                                  ? Colors.grey
                                                  : Colors.blue),
                                          title: Text(_notifications?[index]
                                                  ['subject'] ??
                                              ''),
                                          subtitle: Text(
                                              "${_notifications?[index]['sender']['name'] ?? ''}\n${_notifications?[index]['sender']['timestamp'] ?? ''}"),
                                          onTap: () async {
                                            setState(() {
                                              _notifications?[index]
                                                  ['read_by_user'] = true;
                                              _currentMessage =
                                                  _notifications?[index];
                                            });
                                            http.Response resonce =
                                                await http.get(Uri.parse(
                                                    '$_apiEndpoint/notification/${_notifications?[index]['id']}/read'));
                                            print(resonce.body);
                                          },
                                        );
                                      },
                                    ),
                                  ),
                                ],
                              ),
                            ),
                          ),
                          Column(
                            mainAxisSize: MainAxisSize.max,
                            children: [
                              Container(
                                width: 1000,
                                height: 120,
                                decoration: BoxDecoration(
                                  border: Border(
                                      bottom: BorderSide(color: Colors.black)),
                                ),
                                child: Visibility(
                                  visible: _currentMessage != null,
                                  replacement: Container(),
                                  child: Row(
                                    children: [
                                      CircleAvatar(
                                        child: Image.network(
                                            'https://api.dicebear.com/9.x/notionists/png?seed=' +
                                                (_currentMessage?['sender']
                                                        ['name'] ??
                                                    '')),
                                        radius: 60,
                                      ),
                                      Column(
                                        children: [
                                          Text(
                                              _currentMessage?['sender']
                                                      ['name'] ??
                                                  '',
                                              style: TextStyle(
                                                  fontSize: 20,
                                                  fontWeight: FontWeight.bold)),
                                          Text(
                                              _currentMessage?['sender']
                                                      ['email'] ??
                                                  '',
                                              style: TextStyle(fontSize: 15)),
                                        ],
                                      )
                                    ],
                                  ),
                                ),
                              ),
                              Container(
                                width: 1000,
                                height: 740,
                                padding: EdgeInsets.all(20),
                                child: SingleChildScrollView(
                                  child: Column(
                                    children: [
                                      Text(_currentMessage?['subject'] ?? '',
                                          style: TextStyle(
                                              fontSize: 20,
                                              fontWeight: FontWeight.bold)),
                                      Divider(),
                                      GptMarkdown(
                                          _currentMessage?['message'] ?? ''),
                                    ],
                                  ),
                                ),
                              ),
                            ],
                          )
                        ],
                      )
                    ],
                  ),
                ),
                shadow: BoxShadow(
                  color: Colors.black.withOpacity(0.5),
                  spreadRadius: 5,
                  blurRadius: 7,
                  offset: Offset(0, 3), // changes position of shadow
                ),
                backgroundColor: Colors.grey[50]!,
                onDragBackgroundColor: Colors.grey[200]!,
              ),
            ),
            Indexed(
              index: _windowOrder.indexOf('stock'),
              child: FlutterFloaty(
                isVisible: _windowStocks,
                intrinsicBoundaries: Rect.fromLTWH(
                  0,
                  0,
                  MediaQuery.of(context).size.width,
                  MediaQuery.of(context).size.height,
                ),
                enableAnimation: false,
                height: 900,
                width: 1200,
                initialX: (MediaQuery.of(context).size.width / 2) - 650,
                initialY: (MediaQuery.of(context).size.height / 2) - 550,
                onTap: () {
                  setState(() {
                    _windowOrder.remove('stock');
                    _windowOrder.add('stock');
                  });
                },
                builder: (context) => Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      Container(
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                              colors: [Color(0xFF245DDA), Color(0xFF0D47DB)],
                              begin: Alignment.bottomCenter,
                              end: Alignment.topCenter),
                        ),
                        child: Row(
                          children: [
                            SizedBox(width: 5),
                            Icon(Icons.attach_money, color: Colors.yellow),
                            SizedBox(width: 5),
                            Text('Serenity Stock Terminal',
                                style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 20,
                                    fontStyle: FontStyle.italic)),
                            Spacer(),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.red,
                                borderRadius: BorderRadius.circular(5),
                                border:
                                    Border.all(color: Colors.white, width: 1),
                              ),
                              child: Icon(Icons.close, color: Colors.white),
                            ),
                            SizedBox(width: 5),
                          ],
                        ),
                      ),

                      Expanded(
                        child: Padding(
                          padding: const EdgeInsets.all(12.0),
                          child: SingleChildScrollView(
                            child: ListView.builder(
                              shrinkWrap: true,
                              itemCount: _stocks?.length ?? 0,
                              itemBuilder: (context, index) {
                                return Container(
                                  decoration: BoxDecoration(
                                    border: Border(
                                        bottom: BorderSide(color: Colors.black)),
                                  ),
                                  child: Column(children: [
                                    ListTile(
                                      leading: CircleAvatar(
                                        backgroundColor: Colors.white,
                                        child: Image.network(
                                            'https://raw.githubusercontent.com/davidepalazzo/ticker-logos/refs/heads/main/ticker_icons/' +
                                                (_stocks?[index]['symbol'] ?? '')+'.png', errorBuilder: (context, error, stackTrace) {
                                                  return Container();
                                                }),
                                      ),
                                      title: Text(_stocks?[index]['name'] ?? ''),
                                      subtitle: Text(
                                          '${_stocks?[index]['category'] ?? ''} : ${_stocks?[index]['symbol'] ?? ''}'),
                                      trailing: Row(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Text(
                                              '\£${_stocks?[index]['current_price'] ?? 0}', style: TextStyle(color: _stocks?[index]['direction'] == 'up' ? Colors.green : Colors.red, fontSize: 20)),
                                          Icon(_stocks?[index]['direction'] == 'up' ? Icons.trending_up : Icons.trending_down, color: _stocks?[index]['direction'] == 'up' ? Colors.green : Colors.red),
                                        ],
                                      ),
                                      onTap: () async {
                                        setState(() {
                                          _currentStock = _stocks?[index];
                                        });
                                      },
                                    ),
                                    Row(
                                      children: [
                                        Expanded(
                                          child: Sparkline(
                                            data: _stocks?[index]['history_data'] ?? [],
                                            gridLinelabelPrefix: '\£',
                                            gridLineColor: Colors.grey,
                                            gridLinesEnable: true,
                                            fillMode: FillMode.below,
                                            lineColor: _stocks?[index]['direction'] == 'up' ? Colors.green : Colors.red,
                                            fillColor: _stocks?[index]['direction'] == 'up' ? Colors.green[200]! : Colors.red[200]!,
                                          ),
                                        ),
                                        SizedBox(width: 10),
                                        SizedBox(
                                          width: 110,
                                          child: Column(
                                            mainAxisSize: MainAxisSize.min,
                                            children: [
                                            GestureDetector(
                                              onTap: _getMail,
                                              child: Container(
                                                width: 95,
                                                decoration: BoxDecoration(
                                                  color: Colors.green[900],
                                                ),
                                                child: Column(
                                                  mainAxisAlignment:
                                                  MainAxisAlignment.center,
                                                  mainAxisSize: MainAxisSize.max,
                                                  crossAxisAlignment:
                                                  CrossAxisAlignment.center,
                                                  children: [
                                                    Icon(Icons.file_upload,
                                                        color: Colors.white),
                                                    Text('BUY',
                                                        style: TextStyle(
                                                            color: Colors.white,
                                                            fontSize: 16)),
                                                  ],
                                                ),
                                              ),
                                            ),
                                            GestureDetector(
                                              onTap: _getMail,
                                              child: Container(
                                                width: 95,
                                                decoration: BoxDecoration(
                                                  color: Colors.red[900],
                                                ),
                                                child: Column(
                                                  mainAxisAlignment:
                                                  MainAxisAlignment.center,
                                                  mainAxisSize: MainAxisSize.max,
                                                  crossAxisAlignment:
                                                  CrossAxisAlignment.center,
                                                  children: [
                                                    Icon(Icons.file_download,
                                                        color: Colors.white),
                                                    Text('SELL',
                                                        style: TextStyle(
                                                            color: Colors.white,
                                                            fontSize: 16)),
                                                  ],
                                                ),
                                              ),
                                            ),
                                          ],),
                                        )
                                      ],
                                    ),
                                    SizedBox(height: 30),
                                  ],)
                                );
                              },
                            ),
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
                shadow: BoxShadow(
                  color: Colors.black.withOpacity(0.5),
                  spreadRadius: 5,
                  blurRadius: 7,
                  offset: Offset(0, 3), // changes position of shadow
                ),
                backgroundColor: Colors.grey[50]!,
                onDragBackgroundColor: Colors.grey[200]!,
              ),
            ),
            Indexed(
              index: _windowOrder.indexOf('news'),
              child: FlutterFloaty(
                isVisible: _windowNews,
                intrinsicBoundaries: Rect.fromLTWH(
                  0,
                  0,
                  MediaQuery.of(context).size.width,
                  MediaQuery.of(context).size.height,
                ),
                enableAnimation: false,
                height: 900,
                width: 1200,
                initialX: (MediaQuery.of(context).size.width / 2) - 700,
                initialY: (MediaQuery.of(context).size.height / 2) - 550,
                onTap: () {
                  setState(() {
                    _windowOrder.remove('news');
                    _windowOrder.add('news');
                  });
                },
                builder: (context) => Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      Container(
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                              colors: [Color(0xFF245DDA), Color(0xFF0D47DB)],
                              begin: Alignment.bottomCenter,
                              end: Alignment.topCenter),
                        ),
                        child: Row(
                          children: [
                            SizedBox(width: 5),
                            Icon(Icons.newspaper, color: Colors.yellow),
                            SizedBox(width: 5),
                            Text('Latest News',
                                style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 20,
                                    fontStyle: FontStyle.italic)),
                            Spacer(),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.red,
                                borderRadius: BorderRadius.circular(5),
                                border:
                                    Border.all(color: Colors.white, width: 1),
                              ),
                              child: Icon(Icons.close, color: Colors.white),
                            ),
                            SizedBox(width: 5),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
                shadow: BoxShadow(
                  color: Colors.black.withOpacity(0.5),
                  spreadRadius: 5,
                  blurRadius: 7,
                  offset: Offset(0, 3), // changes position of shadow
                ),
                backgroundColor: Colors.grey[50]!,
                onDragBackgroundColor: Colors.grey[200]!,
              ),
            ),
            Indexed(
              index: _windowOrder.indexOf('chess'),
              child: FlutterFloaty(
                isVisible: _windowChess,
                intrinsicBoundaries: Rect.fromLTWH(
                  0,
                  0,
                  MediaQuery.of(context).size.width,
                  MediaQuery.of(context).size.height,
                ),
                enableAnimation: false,
                height: 540,
                width: 500,
                initialX: (MediaQuery.of(context).size.width / 2) - 700,
                initialY: (MediaQuery.of(context).size.height / 2) - 550,
                onTap: () {
                  clippytContext.callMethod('clippySpeak', ['Hey, this does not look like work, get back to making money!']);
                  setState(() {
                    _windowOrder.remove('chess');
                    _windowOrder.add('chess');
                  });
                },
                builder: (context) => Container(
                  decoration: BoxDecoration(
                    borderRadius: BorderRadius.circular(10),
                  ),
                  clipBehavior: Clip.antiAlias,
                  child: Column(
                    children: [
                      Container(
                        height: 40,
                        decoration: BoxDecoration(
                          gradient: LinearGradient(
                              colors: [Color(0xFF245DDA), Color(0xFF0D47DB)],
                              begin: Alignment.bottomCenter,
                              end: Alignment.topCenter),
                        ),
                        child: Row(
                          children: [
                            SizedBox(width: 5),
                            Icon(Icons.gamepad, color: Colors.yellow),
                            SizedBox(width: 5),
                            Text('Chess',
                                style: TextStyle(
                                    color: Colors.white,
                                    fontSize: 20,
                                    fontStyle: FontStyle.italic)),
                            Spacer(),
                            Container(
                              decoration: BoxDecoration(
                                color: Colors.red,
                                borderRadius: BorderRadius.circular(5),
                                border:
                                Border.all(color: Colors.white, width: 1),
                              ),
                              child: Icon(Icons.close, color: Colors.white),
                            ),
                            SizedBox(width: 5),
                          ],
                        ),
                      ),
                      chess.ChessBoard(
                        controller: controller,
                        boardColor: chess.BoardColor.orange,
                        boardOrientation: chess.PlayerColor.white,
                      )
                    ],
                  ),
                ),
                shadow: BoxShadow(
                  color: Colors.black.withOpacity(0.5),
                  spreadRadius: 5,
                  blurRadius: 7,
                  offset: Offset(0, 3), // changes position of shadow
                ),
                backgroundColor: Colors.grey[50]!,
                onDragBackgroundColor: Colors.grey[200]!,
              ),
            ),
          ]),
        ),
        bottomNavigationBar: Container(
          decoration: BoxDecoration(
            gradient: LinearGradient(
                colors: [Color(0xFF245DDA), Color(0xFF0D47DB)],
                begin: Alignment.bottomCenter,
                end: Alignment.topCenter),
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
          child: Row(
            children: [
              Container(
                width: 150,
                height: double.infinity,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                      colors: [Color(0xFF23AF4E), Color(0xFF1D8A3D)],
                      begin: Alignment.bottomCenter,
                      end: Alignment.topCenter),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Icon(Icons.window_sharp, color: Colors.white),
                    SizedBox(width: 5),
                    Text('stonks',
                        style: TextStyle(
                            color: Colors.white,
                            fontSize: 20,
                            fontStyle: FontStyle.italic)),
                  ],
                ),
              ),
              SizedBox(width: 5),
              Visibility(
                visible: _windowMail,
                child: GestureDetector(
                  onTap: () {
                    setState(() {
                      _windowOrder.remove('mail');
                      _windowOrder.add('mail');
                    });
                  },
                  child: Container(
                    margin: EdgeInsets.symmetric(horizontal: 5, vertical: 3),
                    padding: EdgeInsets.symmetric(horizontal: 10),
                    height: double.infinity,
                    decoration: BoxDecoration(
                      boxShadow: [
                        BoxShadow(
                          color: Colors.white.withOpacity(0.2),
                          spreadRadius: 2,
                          blurRadius: 1,
                          offset: Offset(0, 3), // changes position of shadow
                        ),
                      ],
                      borderRadius: BorderRadius.circular(5),
                      gradient: LinearGradient(
                          colors: [Color(0xFF0D47DB), Color(0xFF072C8A)],
                          begin: Alignment.bottomCenter,
                          end: Alignment.topCenter),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.mail, color: Colors.white),
                        SizedBox(width: 5),
                        Text('E-Mail',
                            style:
                                TextStyle(color: Colors.white, fontSize: 20)),
                      ],
                    ),
                  ),
                ),
              ),
              Visibility(
                visible: _windowStocks,
                child: GestureDetector(
                  onTap: () {
                    setState(() {
                      _windowOrder.remove('stock');
                      _windowOrder.add('stock');
                    });
                  },
                  child: Container(
                    margin: EdgeInsets.symmetric(horizontal: 5, vertical: 3),
                    padding: EdgeInsets.symmetric(horizontal: 10),
                    height: double.infinity,
                    decoration: BoxDecoration(
                      boxShadow: [
                        BoxShadow(
                          color: Colors.white.withOpacity(0.2),
                          spreadRadius: 2,
                          blurRadius: 1,
                          offset: Offset(0, 3), // changes position of shadow
                        ),
                      ],
                      borderRadius: BorderRadius.circular(5),
                      gradient: LinearGradient(
                          colors: [Color(0xFF0D47DB), Color(0xFF072C8A)],
                          begin: Alignment.bottomCenter,
                          end: Alignment.topCenter),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.attach_money, color: Colors.white),
                        SizedBox(width: 5),
                        Text('Serenity Stock Terminal',
                            style:
                                TextStyle(color: Colors.white, fontSize: 20)),
                      ],
                    ),
                  ),
                ),
              ),
              Visibility(
                visible: _windowNews,
                child: GestureDetector(
                  onTap: () {
                    setState(() {
                      _windowOrder.remove('news');
                      _windowOrder.add('news');
                    });
                  },
                  child: Container(
                    margin: EdgeInsets.symmetric(horizontal: 5, vertical: 3),
                    padding: EdgeInsets.symmetric(horizontal: 10),
                    height: double.infinity,
                    decoration: BoxDecoration(
                      boxShadow: [
                        BoxShadow(
                          color: Colors.white.withOpacity(0.2),
                          spreadRadius: 2,
                          blurRadius: 1,
                          offset: Offset(0, 3), // changes position of shadow
                        ),
                      ],
                      borderRadius: BorderRadius.circular(5),
                      gradient: LinearGradient(
                          colors: [Color(0xFF0D47DB), Color(0xFF072C8A)],
                          begin: Alignment.bottomCenter,
                          end: Alignment.topCenter),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.newspaper, color: Colors.white),
                        SizedBox(width: 5),
                        Text('Latest News',
                            style:
                                TextStyle(color: Colors.white, fontSize: 20)),
                      ],
                    ),
                  ),
                ),
              ),
              Visibility(
                visible: _windowChess,
                child: GestureDetector(
                  onTap: () {
                    clippytContext.callMethod('clippySpeak', ['Hey, this does not look like work, get back to making money!']);
                    setState(() {
                      _windowOrder.remove('chess');
                      _windowOrder.add('chess');
                    });
                  },
                  child: Container(
                    margin: EdgeInsets.symmetric(horizontal: 5, vertical: 3),
                    padding: EdgeInsets.symmetric(horizontal: 10),
                    height: double.infinity,
                    decoration: BoxDecoration(
                      boxShadow: [
                        BoxShadow(
                          color: Colors.white.withOpacity(0.2),
                          spreadRadius: 2,
                          blurRadius: 1,
                          offset: Offset(0, 3), // changes position of shadow
                        ),
                      ],
                      borderRadius: BorderRadius.circular(5),
                      gradient: LinearGradient(
                          colors: [Color(0xFF0D47DB), Color(0xFF072C8A)],
                          begin: Alignment.bottomCenter,
                          end: Alignment.topCenter),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.gamepad, color: Colors.white),
                        SizedBox(width: 5),
                        Text('Chess',
                            style:
                            TextStyle(color: Colors.white, fontSize: 20)),
                      ],
                    ),
                  ),
                ),
              ),
              Spacer(),
              GestureDetector(
                onTap: () {
                  clippytContext.callMethod('toggleDarkMode');
                },
                child: Icon(Icons.brightness_6_sharp, color: Colors.white),
              ),
              SizedBox(width: 10),
              Text(_timeString,
                  style: TextStyle(color: Colors.white, fontSize: 20)),
              SizedBox(width: 10),
            ],
          ),
        ),
      ),
    );
  }
}
