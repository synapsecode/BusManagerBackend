import 'dart:io';

import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

Map currentStudent = {
  "session_key": null,
  "id": null,
  "name": null,
  "phone_number": null,
  "home_address": null,
  "location": null,
  "university_name": null,
  "university_address": null
};

Map<String, String> get authHeader =>
    {'Session-Key': currentStudent['session_key']};

String serverURL = "";

startupSequence({
  BuildContext context,
  Widget loginPage,
  Widget homePage,
}) async {
  SharedPreferences prefs = await SharedPreferences.getInstance();
  String sessionKey = prefs.getString('session_key') ?? null;
  String phone = prefs.getString('phone') ?? null;
  if (phone == null || sessionKey == null) {
    //First Time Usage => LoginPage
    Navigator.of(context).pushReplacement(
      MaterialPageRoute(builder: (context) => loginPage),
    );
  } else {
    currentStudent['session_key'] = sessionKey;
    currentStudent['phone_number'] = phone;

    bool sessionActive = await checkSession();
    if (sessionActive) {
      //AutoLogin
      await getStudent(); //Populate Current Student Data
      List payStat = await checkPaymentStatus();
      if (payStat[0]) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (context) => homePage),
        );
      } else {
        showDialog(
          context: context,
          builder: (context) {
            return AlertDialog(
              title: Text("Payment Status Error"),
              content: Container(
                child: Text(payStat[1]),
              ),
              actions: [
                FlatButton(
                  child: Text("Exit"),
                  onPressed: () {
                    exit(0);
                  },
                )
              ],
            );
          },
        );
      }
    } else {
      //InactiveSession => LoginPage
      Navigator.of(context).pushReplacement(
        MaterialPageRoute(builder: (context) => loginPage),
      );
    }
  }
}

//Checks if the User has an Active Session
checkSession() async {
  String phone = currentStudent['phone_number'];
  String sessionKey = currentStudent['session_key'];
  final response = await http.get("$serverURL/checksession/$phone/$sessionKey");
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    if (res['status'] == 200) {
      return res['isActive'];
    }
  }
  return false;
}

//get all the universities {'uni_name', 'uni_address'}
getUniversities() async {
  final response = await http.get('$serverURL/getuniversities');
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    return res['universities'];
  }
  return [];
}

//get all locations
getLocations() async {
  final response = await http.get('$serverURL/getlocations');
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    return res['locations'];
  }
  return [];
}

getStudent() async {
  if (currentStudent['phone_number'] != null &&
      currentStudent['session_key'] != null) {
    final response = await http.get(
      '$serverURL/student/getstudent/${currentStudent['phone_number']}',
      headers: authHeader,
    );

    if (response.statusCode == 200) {
      Map res = json.decode(response.body);
      if (res['status'] == 200) {
        String skey = currentStudent['session_key'];
        currentStudent = res['student'];
        currentStudent['session_key'] = skey;
        SharedPreferences prefs = await SharedPreferences.getInstance();
        print("Saving Data to Shared Prefs");
        await prefs.setString('session_key', skey);
        await prefs.setString('phone_number', currentStudent['phone_number']);
      }
    }
  }
}

//==========================================================================================
//Resend OTP to User
resendOTP() async {
  await http
      .get("$serverURL/student/resend_otp/${currentStudent['phone_number']}");
}

//Verify the Students Phone
verifyStudentPhone(String otp) async {
  final response = await http.get(
    "$serverURL/student/verifyphone/${currentStudent['phone_number']}/$otp",
  );
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    if (res['status'] == 200) return true;
  }
  return false;
}

//Logout
logoutStudent() async {
  await http.get("$serverURL/student/logout/${currentStudent['phone_number']}");
}

registerStudent({
  name,
  phone,
  homeAddress,
  location,
  universityName,
  universityAddress,
}) async {
  Map payload = {
    "name": name,
    "phone_number": phone,
    "home_address": homeAddress,
    "location": location,
    "university_name": universityName,
    "university_address": universityAddress
  };
  final response = await http.post('$serverURL/student/register',
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode(payload));
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    return res;
  }
  return {'status': 0, 'message': 'Register Request Server Error'};
}

login({
  OTP,
  phone,
  post = false,
}) async {
  if (post) {
    final response = await http.post(
      '$serverURL/student/login/$phone',
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode({'otp': OTP}),
    );
    if (response.statusCode == 200) {
      Map res = json.decode(response.body);
      if (res['status'] == 200) {
        print("SessionKey: ${res['session_key']}");
        currentStudent['session_key'] = res['session_key'];
        currentStudent['phone_number'] = phone;
        print("Getting Student Details");
        await getStudent();
        return true;
      }
    }
    return false;
  }
  await http.get('$serverURL/student/login/$phone');
}

getAvailableBuses() async {
  final response = await http.get(
    "$serverURL/student/get_available_buses/${currentStudent['phone_number']}",
    headers: authHeader,
  );
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    if (res['status'] == 200) {
      return res['drivers'];
    }
  }
  return [];
}

checkPaymentStatus() async {
  final response = await http.get(
    "$serverURL/student/checkpaymentstatus/${currentStudent['phone_number']}",
    headers: authHeader,
  );
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    if (res['status'] == 200) {
      return [res['isPaid'], res['message']];
    }
    return [false, res['message']];
  }
  return [false, 'Server Error'];
}

getMyDrivers() async {
  final response = await http.get(
    "$serverURL/student/mydrivers/${currentStudent['phone_number']}",
    headers: authHeader,
  );
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    if (res['status'] == 200) {
      return res['drivers'];
    }
  }
  return [];
}

editProfile({
  name,
  phone,
  homeAddress,
  location,
  universityName,
  universityAddress,
}) async {
  Map payload = {
    "id": currentStudent['id'],
    "name": name ?? currentStudent['name'],
    "phone_number": phone ?? currentStudent['phone_number'],
    "home_address": homeAddress ?? currentStudent['home_address'],
    "location": location ?? currentStudent['location'],
    "university_name": universityName ?? currentStudent['university_name'],
    "university_address":
        universityAddress ?? currentStudent['university_address'],
  };
  final resp = await http.post(
    '$serverURL/student/edit_profile',
    body: jsonEncode(payload),
    headers: {
      ...authHeader,
      'Content-Type': 'application/json; charset=UTF-8',
    },
  );
  if (resp.statusCode == 200) {
    if (phone != currentStudent['phone_number']) {
      //logout procedure navigate to login screen
    } else {
      await getStudent();
    }
  }
}

addRating({String license_number, int rating}) async {
  final response = await http.post(
    '$serverURL/driver/add_rating',
    headers: {
      ...authHeader,
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(
      {
        'license_number': license_number,
        'student_phone': currentStudent['phone_number'],
        'rating': rating,
      },
    ),
  );
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    print(res);
  }
}
