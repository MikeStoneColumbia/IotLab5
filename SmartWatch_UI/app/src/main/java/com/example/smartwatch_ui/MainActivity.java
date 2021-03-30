package com.example.smartwatch_ui;

import androidx.annotation.Nullable;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import android.Manifest;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Location;
import android.location.LocationManager;
import android.os.AsyncTask;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.util.Log;
import android.view.View;
import android.widget.ImageView;
import android.widget.TextView;
import android.widget.Toast;

import com.android.volley.AuthFailureError;
import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.RequestFuture;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.DataInputStream;
import java.io.DataOutputStream;
import java.io.IOException;
import java.net.Socket;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ExecutionException;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.TimeoutException;

import twitter4j.Status;
import twitter4j.Twitter;
import twitter4j.TwitterException;
import twitter4j.TwitterFactory;
import twitter4j.auth.AccessToken;


public class MainActivity extends AppCompatActivity {

    TextView speechOut;
    ImageView mic;
    LocationManager lm;
    Location location;
    String w_link="https://api.openweathermap.org/data/2.5/find?";
    String w_key="&appid=4e8e219db3de74ce6562e6f56a7195d8";
    String tweetLink = "https://api.thingspeak.com/apps/thingtweet/1/statuses/update?api_key=15IGQ29M9K47QQE4&status=";
    String tweetKey = "15IGQ29M9K47QQE4";
    String tweetPath = "apps/thingtweet/1/statuses/update?api_key=";

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        speechOut = findViewById(R.id.specchOut);
        mic = findViewById(R.id.microphone);

        mic.setImageResource(R.drawable.microphone);


        mic.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {

                Intent speech = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
                speech.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
                speech.putExtra(RecognizerIntent.EXTRA_PROMPT, "Give me a command.");
                startActivityForResult(speech, 1);

            }
        });

        lm = (LocationManager) getSystemService(Context.LOCATION_SERVICE);
        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            // TODO: Consider calling
            //    ActivityCompat#requestPermissions
            // here to request the missing permissions, and then overriding
            //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
            //                                          int[] grantResults)
            // to handle the case where the user grants the permission. See the documentation
            // for ActivityCompat#requestPermissions for more details.

            ActivityCompat.requestPermissions(this, new String[]{android.Manifest.permission.ACCESS_FINE_LOCATION},PackageManager.PERMISSION_GRANTED);
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_COARSE_LOCATION},PackageManager.PERMISSION_GRANTED);
        }
        location = lm.getLastKnownLocation(LocationManager.GPS_PROVIDER);

    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, @Nullable Intent data) {
        super.onActivityResult(requestCode, resultCode, data);

        if(requestCode == 1 && resultCode == RESULT_OK){

            String command = data.getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS).get(0).toString();
            speechOut.setText(command);
            handleAPI(command);

        }

    }

    public void handleAPI(String data){

        if(data.contains("tweet")){
            Log.d("tweetStatus", "attempting to tweet: " + data.substring(6));
            sendTweet(data.substring(6));
        }

        else if(data.contains("get weather")){
            getWeather();
        }

        else if(data.contains("display time")){
            sendToHuzzah("","time");
        }

        else {
            sendToHuzzah("","");
        }

    }

    public void getWeather(){
        RequestQueue requestQueue = Volley.newRequestQueue(this);
        double longitude = location.getLongitude();
        double latitude = location.getLatitude();
        String cor = "lat=" + latitude + "&lon=" + longitude;

        Log.d("reqLink",w_link+cor+w_key +'\n');
        System.out.println("outside");

        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, w_link+cor+w_key, null, new Response.Listener<JSONObject>() {
            @Override
            public void onResponse(JSONObject response) {
                try {
                    System.out.println("inside");
                    JSONObject res = response.getJSONArray("list").getJSONObject(0);
                    String weatherDesc = res.getJSONArray("weather").getJSONObject(0).getString("description");
                    String temp = (Math.round(res.getJSONObject("main").getDouble("temp") - 273.15)) + "";
                    Log.d("reqlink", temp);
                    String data = weatherDesc +'%' + temp + " Celsius";
                    sendToHuzzah(data,"weather");
                } catch (JSONException e) {
                    e.printStackTrace();
                    Log.d("tester", "Unpacking Json failed");
                }

            }
        }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                System.out.println("error");
                error.printStackTrace();
            }
        });
        requestQueue.add(jsonObjectRequest);

    }

    public void sendTweet(String msg){
       // RequestQueue requestQueue = Volley.newRequestQueue(this);

//        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.GET, tweetLink+msg, null, new Response.Listener<JSONObject>() {
//            @Override
//            public void onResponse(JSONObject response) {
//                Log.d("tweetStatus", "tweeted");
//            }
//        }, new Response.ErrorListener() {
//            @Override
//            public void onErrorResponse(VolleyError error) {
//                Log.d("tweetStatus", "Error: " + error.getMessage());
//                error.printStackTrace();
//            }
//        }){
//            @Override
//            public String getBodyContentType() {
//                return "application/x-www-form-urlencoded; charset=UTF-8";
//            }
//
//            @Override
//            protected Map<String, String> getParams() throws AuthFailureError {
//                Map<String,String> params =  new HashMap<>();
//                params.put("api_key",tweetKey);
//                params.put("status",msg);
//                return params;
//            }
//
//        };

        //requestQueue.add(jsonObjectRequest);


        Twitter twitter = TwitterFactory.getSingleton();
        twitter.setOAuthConsumer("ZiHimAKxbOsynDsfTdLsjC9VK","kCxjMVdLwHTxSkZVAfGx4Jn89OkWokT0ZkEKg93LysCT37pSRq");
        AccessToken accessToken = new AccessToken("1149385301090959360-uxJMxm8a6SFtQqws61X0ZN3e1xxiTa","9s1I9NEopx2Iy0Gslv6V2WhMRw3aPTsaRgYvfzB2d03Gq");
        twitter.setOAuthAccessToken(accessToken);
        try {
            twitter.updateStatus("testing");
        } catch (TwitterException e) {
            e.printStackTrace();
        }


    }

    public void sendToHuzzah(String data, String command){

        String url = "https://4cd598a0468b.ngrok.io";
        JSONObject jsonCommand = new JSONObject();
        DateFormat df =  new SimpleDateFormat("yy/MM/dd HH:mm:ss");
        Date dateobj = new Date();
        StringBuilder completeDate = new StringBuilder();
        String rawDate = df.format(dateobj).toString();
        String[] compDate = rawDate.split(" ");
        String[] yearMonthDay = compDate[0].split("/");
        yearMonthDay[0] = "20" + yearMonthDay[0];
        for(String spec: yearMonthDay){
            completeDate.append(spec);
            completeDate.append(':');
        }

        //completeDate.deleteCharAt(completeDate.length()-1);
        completeDate.append(compDate[1]);
        Log.d("datetime",completeDate.toString());
        try {
            jsonCommand.put("time", completeDate.toString());
            jsonCommand.put("command", command);
            jsonCommand.put("data",data);

        } catch (JSONException e) {
            e.printStackTrace();
        }

        Log.d("tester","I am here");
        JsonObjectRequest jsonObjectRequest = new JsonObjectRequest(Request.Method.POST, url, jsonCommand, new Response.Listener<JSONObject>() {
            @Override
            public void onResponse(JSONObject response) {
                try {
                    Log.d("tester", "huzzah response: " + response.toString());
                    Toast.makeText(getApplicationContext(),"huzzah response: " + response.getString("response"), Toast.LENGTH_LONG).show();
                } catch (JSONException e) {
                    e.printStackTrace();
                    Log.d("tester", "Unpacking Json failed");
                }

            }
        }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                error.printStackTrace();
            }
        });

        Log.d("tester","I here");
        RequestQueue requestQueue = Volley.newRequestQueue(this);
        requestQueue.add(jsonObjectRequest);
    }
}