import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;

void main() async {
  var resp = await http.get(Uri.http("localhost:3005", "/auth/register"));
  runApp(const MyApp());
  print(resp.body);
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  static const String _title = 'Minerva';

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
        title: "Minerva",
        theme: ThemeData(
          brightness: Brightness.dark,
          primaryColor: Colors.amber[500],
        ),
        home: const HomePage());
  }
}

class HomePage extends StatelessWidget {
  const HomePage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
        appBar: AppBar(
          title: const Text('Minerva'),
          backgroundColor: Theme.of(context).primaryColor,
        ),
        body: SafeArea(
            child: Center(
                child: Column(
          children: [
            // image
            const Image(
                image: AssetImage('images/brewery.jpg'),
                height: 400,
                width: 400),

            // spacer
            SizedBox(height: 10),

            // form
            MyForm(),

            // spacer
            SizedBox(height: 10),

            // divider
          ],
        ))));
  }
}

class MyForm extends StatefulWidget {
  MyForm({super.key});

  @override
  State<MyForm> createState() => _MyFormState();
}

class _MyFormState extends State<MyForm> {
  final TextEditingController orgController = TextEditingController();
  final TextEditingController emailController = TextEditingController();
  final TextEditingController passwordController = TextEditingController();

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Padding(
            padding: EdgeInsets.symmetric(horizontal: 50),
            child: TextField(
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Enter your organization',
              ),
              controller: orgController,
            )),
        SizedBox(height: 10),
        Padding(
            padding: EdgeInsets.symmetric(horizontal: 50),
            child: TextField(
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Enter your email',
              ),
              controller: emailController,
            )),
        SizedBox(height: 10),
        Padding(
            padding: EdgeInsets.symmetric(horizontal: 50),
            child: TextField(
              decoration: InputDecoration(
                border: OutlineInputBorder(),
                hintText: 'Enter your password',
              ),
              controller: passwordController,
              obscureText: true,
            )),
        // submit button
        SizedBox(height: 10),
        ElevatedButton(
            onPressed: () {
              post({
                "organization": orgController.text,
                "username": emailController.text,
                "password": passwordController.text
              });
              for (TextEditingController con in [
                orgController,
                emailController,
                passwordController
              ]) {
                con.clear();
              }
            },
            child: Text(
              'Submit',
            ),
            style: ElevatedButton.styleFrom(backgroundColor: Colors.amber[400]))
      ],
    );
  }
}

void post(Map<String, String> postBody) async {
  try {
    var response = await http.post(Uri.http('localhost:3005', '/auth/register'),
        body: postBody);
  } catch (e) {
    print(e.toString());
  }
}
