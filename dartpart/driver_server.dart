import 'package:flutter/material.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

Map currentDriver = {
  'id': null,
  'session_key': null,
  'name': null,
  'phone_number': null,
  'bus_number': null,
  'license_number': null,
  'experience': null,
  'rating': null,
  'image': null,
  'phone_verified': null,
  'verified': null,
  'location': null,
};

Map<String, String> get authHeader =>
    {'Session-Key': currentDriver['session_key']};

String serverURL = "";

//Checks if the User has an Active Session
checkSession() async {
  String phone = currentDriver['phone_number'];
  String sessionKey = currentDriver['session_key'];
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

getDriver() async {
  if (currentDriver['phone_number'] != null &&
      currentDriver['session_key'] != null) {
    final response = await http.get(
      '$serverURL/driver/getdriver/${currentDriver['phone_number']}',
      headers: authHeader,
    );

    if (response.statusCode == 200) {
      Map res = json.decode(response.body);
      if (res['status'] == 200) {
        String skey = currentDriver['session_key'];
        currentDriver = res['driver'];
        currentDriver['session_key'] = skey;
        SharedPreferences prefs = await SharedPreferences.getInstance();
        print("Saving Data to Shared Prefs");
        await prefs.setString('session_key', skey);
        await prefs.setString('phone_number', currentDriver['phone_number']);
      }
    }
  }
}

resendOTP() async {
  await http
      .get("$serverURL/driver/resend_otp/${currentDriver['phone_number']}");
}

//Verify the drivers Phone
verifyDriverPhone(String otp) async {
  final response = await http.get(
    "$serverURL/driver/verifyphone/${currentDriver['phone_number']}/$otp",
  );
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    if (res['status'] == 200) return true;
  }
  return false;
}

//Logout
logoutDriver() async {
  await http.get("$serverURL/driver/logout/${currentDriver['phone_number']}");
}

register({
  name,
  phone,
  bus_number,
  location,
  license_number,
  experience,
}) async {
  Map payload = {
    "name": name,
    "phone_number": phone,
    "bus_number": bus_number,
    "location": location,
    "license_number": license_number,
    "experience": experience
  };
  final response = await http.post(
    '$serverURL/driver/register',
    headers: <String, String>{
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(payload),
  );
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
      '$serverURL/driver/login/$phone',
      headers: <String, String>{
        'Content-Type': 'application/json; charset=UTF-8',
      },
      body: jsonEncode({'otp': OTP}),
    );
    if (response.statusCode == 200) {
      Map res = json.decode(response.body);
      if (res['status'] == 200) {
        print("SessionKey: ${res['session_key']}");
        currentDriver['session_key'] = res['session_key'];
        currentDriver['phone_number'] = phone;
        print("Getting driver Details");
        await getDriver();
        return true;
      }
    }
    return false;
  }
  await http.get('$serverURL/driver/login/$phone');
}

allowStudent({String studentID, Function errorDialogBuilder}) async {
  final response = await http.post(
    '$serverURL/driver/add_rating',
    headers: {
      ...authHeader,
      'Content-Type': 'application/json; charset=UTF-8',
    },
    body: jsonEncode(
      {
        'student_id': studentID,
        'license_number': currentDriver['license_number'],
      },
    ),
  );
  if (response.statusCode == 200) {
    Map res = json.decode(response.body);
    if (res['status'] == 0) {
      errorDialogBuilder(res['message']);
      return false;
    } else {
      return false;
    }
  }
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
    "id": currentDriver['id'],
    "name": name ?? currentDriver['name'],
    "phone_number": phone ?? currentDriver['phone_number'],
    "bus_number": homeAddress ?? currentDriver['bus_number'],
    "location": location ?? currentDriver['location'],
    "license_number": universityName ?? currentDriver['license_number'],
    "experience": universityAddress ?? currentDriver['experience'],
  };
  final resp = await http.post(
    '$serverURL/driver/edit_profile',
    body: jsonEncode(payload),
    headers: {
      ...authHeader,
      'Content-Type': 'application/json; charset=UTF-8',
    },
  );
  if (resp.statusCode == 200) {
    if (phone != currentDriver['phone_number']) {
      //logout procedure navigate to login screen
    } else {
      await getDriver();
    }
  }
}

editProfileImage(pFile) async {
  String url =
      "$serverURL/driver/update_profile_image/${currentDriver['phone_number']}";
  final request = http.MultipartRequest('POST', Uri.parse(url));
  request.files.add(
    await http.MultipartFile.fromPath(
      'picture',
      pFile.path,
    ),
  );
  request.headers.addAll(authHeader);
  final response = await request.send();
  if (response.statusCode == 200) {
    print(response);
    return;
  }
  print(response);
}
