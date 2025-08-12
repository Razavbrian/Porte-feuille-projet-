package com.example.myapplication.activity

import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import android.widget.TextView
import androidx.recyclerview.widget.RecyclerView
import com.example.myapplication.R

class PresenceAdapter(private val presenceList: List<Presence>) :
    RecyclerView.Adapter<PresenceAdapter.PresenceViewHolder>() {
    class PresenceViewHolder(itemView: View) : RecyclerView.ViewHolder(itemView) {
        val nomTextView: TextView = itemView.findViewById(R.id.titleNom)
        val serviceTextView: TextView = itemView.findViewById(R.id.titleService)
        val dateTextView: TextView = itemView.findViewById(R.id.titleDate)
    }
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): PresenceViewHolder {
        val view = LayoutInflater.from(parent.context)
            .inflate(R.layout.item_presence, parent, false)
        return PresenceViewHolder(view)
    }

    override fun onBindViewHolder(holder: PresenceAdapter.PresenceViewHolder, position: Int) {
        val presence = presenceList[position]
        holder.nomTextView.text = presence.nom
        holder.serviceTextView.text = presence.service
        holder.dateTextView.text = presence.date
    }

    override fun getItemCount() = presenceList.size


}
