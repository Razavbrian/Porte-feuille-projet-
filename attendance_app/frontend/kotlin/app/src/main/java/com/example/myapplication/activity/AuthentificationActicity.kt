package com.example.myapplication.activity

import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity

import com.example.myapplication.R


import com.google.android.material.button.MaterialButton
import com.google.android.material.textfield.TextInputLayout
import retrofit2.Call
import retrofit2.Response
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import retrofit2.http.Body
import retrofit2.http.POST

class AuthentificationActicity : AppCompatActivity() {
    lateinit var textInputLayoutName: TextInputLayout
    lateinit var textInputLayoutPassword: TextInputLayout
    lateinit var btnconnect: MaterialButton
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_authentification_acticity)

            textInputLayoutName = findViewById(R.id.layoutTextInputName)
            textInputLayoutPassword = findViewById(R.id.layoutTextInpuPassword)
            btnconnect = findViewById(R.id.btnconnect)
            btnconnect.setOnClickListener {
                textInputLayoutName.isErrorEnabled = false
                textInputLayoutPassword.isErrorEnabled = false
                val username = textInputLayoutName.editText?.text.toString()
                val password = textInputLayoutPassword.editText?.text.toString()
                if (username.isEmpty() || password.isEmpty()){
                    if(username.isEmpty()){
                        textInputLayoutName.error = "Le Nom d'utilisateur est resquis"
                        textInputLayoutName.isErrorEnabled = true
                    }
                    if(password.isEmpty()){
                        textInputLayoutPassword.error = "Le mot de passe est resquis"
                        textInputLayoutPassword.isErrorEnabled = true
                    }
                }else{
                    signIn(username, password)
                }
            }
        }
    fun signIn(username:String, password:String){
        val apiService = ApiClient.create()
        val loginRequest = LoginRequest(username, password)

        apiService.login(loginRequest).enqueue(object : retrofit2.Callback<LoginResponse>{
            override fun onResponse(call: Call<LoginResponse>, response: Response<LoginResponse>){
                if (response.isSuccessful){
                    Log.d("signIn", "Login successful: ${response.body()?.token}")
                    val intent = Intent(this@AuthentificationActicity, Home_Activity::class.java)
                    intent.putExtra("token", response.body()?.token)  // Optionally pass the token
                    startActivity(intent)
                    finish()
                }else{
                    Log.d("signIn", "Login failed: ${response.message()}")

                }
            }
            override fun onFailure(call: Call<LoginResponse>, t: Throwable) {
                Log.d("signIn", "Error: ${t.message}")
            }
        })


    }
}
interface ApiService {
    @POST("api/login/")  // endpoint
    fun login(@Body request: LoginRequest): Call<LoginResponse>
}
object ApiClient {
    private const val BASE_URL = "http://192.168.10.224:8000/"

    fun create(): ApiService {
        val retrofit = Retrofit.Builder()
            .baseUrl(BASE_URL)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
        return retrofit.create(ApiService::class.java)
    }
}

data class LoginResponse(
    val token: String
    )

data class LoginRequest (
    val username: String,
    val password: String

    )


