package com.example.myapplication.activity

import android.app.AlertDialog
import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.view.Menu
import android.view.MenuItem
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.activity.enableEdgeToEdge
import androidx.appcompat.app.AppCompatActivity
import androidx.recyclerview.widget.LinearLayoutManager
import androidx.recyclerview.widget.RecyclerView
import com.example.myapplication.R
import okhttp3.Call
import okhttp3.Callback
import okhttp3.MediaType.Companion.toMediaTypeOrNull
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody
import okhttp3.Response
import org.json.JSONArray
import org.json.JSONObject
import java.io.IOException
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

class Home_Activity : AppCompatActivity() {
    private val client = OkHttpClient()
    private val presencesList = mutableListOf<Presence>()
    private lateinit var adapter: PresenceAdapter
    companion object {
        const val ZXING_REQUEST_CODE = 100  // Code de requête pour l'Intent
    }
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContentView(R.layout.activity_home)
        //titre tableau
        val textViewTitle = findViewById<TextView>(R.id.textView)
        val currentDate = SimpleDateFormat("dd/MM/yyyy", Locale.getDefault()).format(Date())
        textViewTitle.text = "Liste des présences du $currentDate"
        //recicleview
        val recyclerView = findViewById<RecyclerView>(R.id.recyclerViewPresence)
        recyclerView.layoutManager = LinearLayoutManager(this)
        adapter = PresenceAdapter(presencesList)
        recyclerView.adapter = adapter

        //bouton scan
        val buttonScan = findViewById<Button>(R.id.bouttonScan)
        buttonScan.setOnClickListener {
            startQRCodeScanner()
        }
    }



    private fun showEmptyFieldsErrorDialog() {
        AlertDialog.Builder(this)
            .setTitle("Erreur")
            .setMessage("Veuillez remplir tous les champs.")
            .setPositiveButton("OK", null)
            .create()
            .show()
    }

    private fun showEmployeeNotFoundDialog(nom: String, poste: String) {
        AlertDialog.Builder(this)
            .setTitle("Erreur")
            .setMessage("L'employé $nom ($poste) n'existe pas.")
            .setPositiveButton("OK", null)
            .create()
            .show()
    }

    private fun startQRCodeScanner() {
        try {
            val intent = Intent("com.google.zxing.client.android.SCAN")
            intent.putExtra("SCAN_MODE", "QR_CODE_MODE") // On précise que l'on veut scanner un QR code
            startActivityForResult(intent, ZXING_REQUEST_CODE)
        } catch (e: Exception) {
            // Si ZXing Barcode Scanner n'est pas installé, on peut rediriger vers Google Play pour installer l'application
            val playStoreIntent = Intent(Intent.ACTION_VIEW)
            playStoreIntent.data = android.net.Uri.parse("market://details?id=com.google.zxing.client.android")
            startActivity(playStoreIntent)
        }
    }

    override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
        super.onActivityResult(requestCode, resultCode, data)
        if (requestCode == ZXING_REQUEST_CODE && resultCode == RESULT_OK) {
            val result = data?.getStringExtra("SCAN_RESULT")  // Récupérer le contenu du QR code
            result?.let {
                Log.d("QRContent", "QR code content: $it")
                // Afficher le résultat du scan (ici, vous pouvez traiter les données scannées)
                val regex = Regex("""Nom:\s*([^,]+),\s*Prénom:\s*([^,]+),\s*Matricule:\s*([^,]+),\s*Service:\s*([^,]+),\s*Fonction:\s*([^,]+),\s*Direction:\s*([^,]+)""")
                val matchResult = regex.find(it)

                if (matchResult != null) {
                    val nom = matchResult.groupValues[1].trim()
                    val matricule = matchResult.groupValues[3].trim()  // Extrait le matricule
                    val service = matchResult.groupValues[4].trim()  // Extrait


                    getEmployeeId(matricule) { employeeId ->
                        if (employeeId != null) {
                            // Enregistrer la présence
                            savePresence(employeId = employeeId, nom = nom, service = service)
                        }
                    }
                }else{
                    // Format incorrect du QR code
                    println("Format du QR code incorrect")
                }
            }
        }
    }

    private fun savePresence(employeId: Int, nom: String, service: String) {
        val url = "http://192.168.10.224:8000/api/attendances/"
        val currentDate = SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.getDefault()).format(Date())
        val json = JSONObject().apply {
            put("employee_id", employeId)
            put("date", currentDate)
        }
        val requestBody = RequestBody.create("application/json".toMediaTypeOrNull(), json.toString())
        val request = Request.Builder().url(url).post(requestBody).build()
        client.newCall(request).enqueue(object : Callback{
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    runOnUiThread {
                        val presence = Presence(nom, service, currentDate)
                        presencesList.add(presence)
                        adapter.notifyDataSetChanged()  // Mettre à jour la liste
                    }
                }
            }

        })

    }

    private fun getEmployeeId(matricule: String, callback: (Int?) -> Unit) {
        val url = "http://192.168.10.224:8000/api/employees?matricule=$matricule"
        val request = Request.Builder().url(url).build()
        client.newCall(request).enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                e.printStackTrace()
                runOnUiThread { callback(null) }
            }

            override fun onResponse(call: Call, response: Response) {
                if (response.isSuccessful) {
                    response.body?.string()?.let { json ->
                        val jsonArray = JSONArray(json)
                        if (jsonArray.length() > 0) {
                            var employeeId: Int? = null
                            // Parcourir tous les employés pour trouver celui qui correspond au nom
                            for (i in 0 until jsonArray.length()) {
                                val employee = jsonArray.getJSONObject(i)
                                // Vérifier si la clé "nom" existe avant d'y accéder
                                if (employee.has("matricule")) {
                                    val employeeMat = employee.getString("matricule")
                                    if (employeeMat.equals(matricule, ignoreCase = true)) {
                                        employeeId = employee.getInt("id")
                                        break // Trouvé, on peut arrêter la boucle
                                    }
                                } else {
                                    Log.e("API Response", "La clé 'nom' est manquante pour l'employé à l'index $i")
                                }
                            }
                            if (employeeId != null) {
                                runOnUiThread { callback(employeeId) }
                            } else {
                                runOnUiThread { callback(null) }  // Aucun employé avec ce nom
                            }
                        } else {
                            runOnUiThread { callback(null) }  // Aucune donnée
                        }
                    }
                } else {
                    runOnUiThread { callback(null) }
                }
            }
        })
    }

    override fun onCreateOptionsMenu(menu: Menu?): Boolean {
        menuInflater.inflate(R.menu.menu_home, menu)
        return super.onCreateOptionsMenu(menu)
    }

    override fun onOptionsItemSelected(item: MenuItem): Boolean {
        if(item.itemId == R.id.itemLogOut){
            finish()
            Intent(this, AuthentificationActicity :: class.java).also{
                startActivity(it)
            }
        }
        return super.onOptionsItemSelected(item)
    }


}


