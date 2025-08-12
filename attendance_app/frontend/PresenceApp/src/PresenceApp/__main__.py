import io
import os
import qrcode
import platform
import datetime
from PIL import Image
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import zxing
import pytz
from plyer import camera
import base64
import toga
import tempfile
from datetime import datetime, date
from toga import icons
from toga.style import Pack
from toga.style.pack import COLUMN, ROW, CENTER
from itertools import cycle
import requests
from reportlab.pdfgen import canvas
import pandas as pd
import platform
if platform.system()=="Linux":
    from rubicon.java import JavaClass

API_BASE_URL = "http://192.168.43.82:8000/api"

class AttendanceApp(toga.App):
    def startup(self):
        """Initialisation de l'application"""
        self.menu_created = False
        self.is_authenticated = False

         # Mode sombre par défaut
        self.is_dark_mode = True
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_box = toga.Box(style=Pack(direction=COLUMN, padding=20,alignment=CENTER))
        self.show_login_screen()
        # Fenêtre principale
        self.main_window.content = self.main_box
        self.main_window.show()

    def create_menu_bar(self):
        """Créer une barre des menus avec un bouton de déconnexion"""
        self.clear_menu_bar()
        # Créer un menu principal avec le bouton de déconnexion
        # Groupe de menu pour le compte utilisateur

        account_menu = toga.Group("Compte")

        # Ajouter la commande de déconnexion avec l'icône de fermeture
        logout_cmd = toga.Command(
            self.logout,
            text="Déconnexion",
            icon='/Users/cbrian/Desktop/Attendance/attendance_app/frontend/PresenceApp/src/PresenceApp/log-out.png',  # Icône de fermeture appropriée pour la déconnexion
            group=account_menu,
            shortcut="Cmd+D"
        )

        # Ajouter l'élément de déconnexion à la barre des menus
        self.main_window.toolbar.add(logout_cmd)

        # Marquer que la barre de menu a été créée
        self.menu_created = True

    def clear_menu_bar(self):
        """Supprime tous les éléments de la barre de menu"""
        self.main_window.toolbar.clear()

    def show_login_screen(self):
        """Affiche le formulaire de connexion pour authentification"""
        self.clear_menu_bar()
        self.main_box.clear()
        # Titre du formulaire
        title_label = toga.Label("Connexion", style=Pack(font_size=24, padding_bottom=20, text_align=CENTER))

        # Champs de texte stylisés pour le nom d'utilisateur et le mot de passe
        self.username_input = toga.TextInput(placeholder="Nom d'utilisateur", style=Pack(padding=(5, 10), width=250))
        self.password_input = toga.PasswordInput(placeholder="Mot de passe", style=Pack(padding=(5, 10), width=250))

        # Bouton de connexion stylisé
        login_button = toga.Button("Se connecter", on_press=self.authenticate_user, style=Pack(padding=(10, 5), font_size=16, background_color="#1E90FF", color="white", width=250))

        # Ajouter les éléments au conteneur principal
        self.main_box.add(title_label)
        self.main_box.add(self.username_input)
        self.main_box.add(self.password_input)
        self.main_box.add(login_button)
        self.main_window.toolbar.visible = False

    def authenticate_user(self, widget):
        """Authentifier l'utilisateur avec l'API backend"""
        username = self.username_input.value
        password = self.password_input.value
        data = {"username": username, "password": password}

        # Appel à l'API pour vérifier les identifiants
        response = requests.post(f"{API_BASE_URL}/login/", data=data)
        if response.status_code == 200:
            self.is_authenticated = True
            self.create_home_screen()  # Affiche l'interface principale
        else:
            self.main_window.error_dialog("Erreur", "Nom d'utilisateur ou mot de passe incorrect")

    def request_permissions(self):
        """Demander les permissions nécessaires pour utiliser la caméra et le stockage"""
        permissions_list = [
            "android.permission.CAMERA",
            "android.permission.WRITE_EXTERNAL_STORAGE"
        ]
        # Utiliser AndroidActivity pour demander des permissions
        activity = self._impl.native  # Utiliser l'instance d'activité actuelle
        permission_granted = True
        for permission in permissions_list:
            if not JavaClass('androidx.core.content.ContextCompat').checkSelfPermission(activity, permission):
                permission_granted = False
                break

        if not permission_granted:
            # Demande de permissions
            JavaClass('androidx.core.app.ActivityCompat').requestPermissions(
                activity,
                permissions_list,
                1  # Code de demande
            )
        else:
            print("Toutes les permissions nécessaires ont été accordées.")

    def permission_callback(self, permissions, grant_results):
            """Gestion des résultats de la demande de permission"""
            for permission, result in zip(permissions, grant_results):
                if result == 0:  # Permission accordée
                    print(f"Permission accordée : {permission}")
                else:  # Permission refusée
                    print(f"Permission refusée : {permission}")
    def toggle_theme(self, widget):
        """Basculer entre le mode sombre et le mode clair"""
        if self.is_dark_mode:
            self.main_box.style.background_color = "white"
            self.is_dark_mode = False
        else:
            self.main_box.style.background_color = "black"
            self.is_dark_mode = True

        self.create_home_screen()

    #écran d'accueil principale
    def create_home_screen(self,widget=None):
        """Écran d'accueil avec options principales"""
        self.main_box.clear()
        # Ajouter la barre des menus avec le bouton de déconnexion
        self.create_menu_bar()
        welcome_label = toga.Label("Bienvenue dans l'application de gestion de présence", style=Pack(padding=10))
        add_employee_button = toga.Button('Ajouter Employé', on_press=self.show_add_employee_screen, style=self.button_style())
        list_employees_button = toga.Button('Voir la Liste des Employés', on_press=self.show_employee_list, style=self.button_style())
        list_presences_button = toga.Button('Voir la Liste des Présences', on_press=self.view_presences, style=self.button_style())


        self.main_box.add(welcome_label)
        self.main_box.add(add_employee_button)
        self.main_box.add(list_employees_button)
        self.main_box.add(list_presences_button)
        image = toga.Image("/Users/cbrian/Desktop/Attendance/attendance_app/frontend/PresenceApp/src/PresenceApp/MEH1.jpeg")

        self.image_view = toga.ImageView(image=image,style=Pack(height=200, width=700, padding_top=10))
        self.main_box.add(self.image_view)

    def clear_specific_menu(self):
        """Supprime tout menu spécifique, mais laisse le menu principal intact s'il a été créé"""
        if self.menu_created:
            self.clear_menu_bar()
            self.create_menu_bar()

    def logout(self, widget):
        """Déconnexion de l'utilisateur et retour à l'écran de connexion"""
        self.is_authenticated = False
        self.show_login_screen()  # Retour à l'écran de connexion

    def button_style(self):
        """Styliser les boutons pour un design moderne"""
        return Pack(padding=10, font_size=14)

    #formulaire d'ajout des employés
    def show_add_employee_screen(self, widget=None):
        """Formulaire pour ajouter un employé"""
        self.main_box.clear()

        # Conteneur pour centrer le formulaire
        form_box = toga.Box(style=Pack(direction=COLUMN, alignment=CENTER, padding=20))

        # Titre du formulaire avec style
        title_label = toga.Label(
            "Ajouter un nouvel employé",
            style=Pack(font_size=20, padding_bottom=15, text_align=CENTER)
        )
        form_box.add(title_label)

        # Champs de texte avec style pour plus de visibilité
        self.name_input = toga.TextInput(
            placeholder="Nom de l'employé",
            style=Pack(width=300, padding=(5, 10))
        )
        self.firstname_input = toga.TextInput(
            placeholder="Prénom de l'employé",
            style=Pack(width=300, padding=(5, 10))
        )
        self.matricule_input = toga.TextInput(
            placeholder="Matricule de l'employé",
            style=Pack(width=300, padding=(5, 10))
        )
        self.departement_input = toga.TextInput(
            placeholder="Département de l'employé",
            style=Pack(width=300, padding=(5, 10))
        )
        self.position_input = toga.TextInput(
            placeholder="Poste de l'employé",
            style=Pack(width=300, padding=(5, 10))
        )

        # Bouton Ajouter avec un style amélioré
        submit_button = toga.Button(
            "Ajouter",
            on_press=self.generate_qr_code,
            style=Pack(width=150, padding=(10, 5), background_color="#4CAF50", color="white", font_size=14)
        )

        # Bouton Retour avec un style similaire pour la cohérence
        back_button = toga.Button(
            "Retour",
            on_press=self.create_home_screen,
            style=Pack(width=150, padding=(10, 5), background_color="#f44336", color="white", font_size=14)
        )

        # Ajouter les champs et boutons au conteneur du formulaire
        form_box.add(self.name_input)
        form_box.add(self.firstname_input)
        form_box.add(self.matricule_input)
        form_box.add(self.departement_input)
        form_box.add(self.position_input)
        form_box.add(submit_button)
        form_box.add(back_button)

        # Ajouter le conteneur form_box à la main_box pour l'affichage
        self.main_box.add(form_box)


    def generate_qr_code(self, widget):
        """Générer un QR code et afficher les informations avant confirmation"""
        name = self.name_input.value
        firstname = self.firstname_input.value
        matricule = self.matricule_input.value
        departement = self.departement_input.value
        position = self.position_input.value

        if name and position:
            # Générer un QR code basé sur le nom et le poste
            qr_data = f"Nom: {name}, Prénom: {firstname}, Matricule: {matricule}, Département: {departement}, Poste: {position}"
            qr_img = qrcode.make(qr_data)

            # Sauvegarder l'image QR dans la mémoire
            temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            qr_img.save(temp_file, format="PNG")
            temp_file.close()

            self.qr_code_image_path = temp_file.name
            # Afficher les informations et le QR code
            self.display_employee_confirmation(name, firstname, matricule, departement, position, self.qr_code_image_path)
        else:
            self.main_window.error_dialog("Erreur", "Veuillez remplir tous les champs.")

    def display_employee_confirmation(self, name, firstname, matricule, departement, position, qr_img):
        """Affiche le nom, poste et le QR code avec options de confirmation ou refus"""
        self.main_box.clear()

        # Convertir le QR code en image et l'afficher dans l'interface
        img_label = toga.ImageView(image=toga.Image(qr_img), style=Pack(width=100, height=100))

        name_label = toga.Label(f"Nom : {name}", style=Pack(padding=10))
        firstname_label = toga.Label(f"Prénom : {firstname}", style=Pack(padding=10))
        matricule_label = toga.Label(f"Matricule : {matricule}", style=Pack(padding=10))
        department_label = toga.Label(f"Département : {departement}", style=Pack(padding=10))
        position_label = toga.Label(f"Poste : {position}", style=Pack(padding=10))
        confirm_button = toga.Button("Confirmer", on_press=lambda w: self.confirm_employee(name, firstname, matricule, position, departement, self.qr_code_image_path))
        refuse_button = toga.Button("Refuser", on_press=self.show_add_employee_screen)

        back_button = toga.Button("Retour", on_press=self.create_home_screen)
        # Ajouter les widgets à la box principale
        self.main_box.add(name_label)
        self.main_box.add(firstname_label)
        self.main_box.add(matricule_label)
        self.main_box.add(department_label)
        self.main_box.add(position_label)
        self.main_box.add(img_label)
        self.main_box.add(confirm_button)
        self.main_box.add(refuse_button)

    def confirm_employee(self, name, firstname, matricule, position, departement, qr_code_image):
        """Confirmer l'ajout de l'employé et envoyer les données au backend"""
        # Créer les données à envoyer au backend, y compris le QR code
        with open(self.qr_code_image_path, "rb") as qr_file:
            qr_code_data = qr_file.read()
        data = {
            'name': name,
            'firstname': firstname,
            'matricule': matricule,
            'position': position,
            'departement': departement,
            'qr_code': qr_code_data  # Vous devrez peut-être ajuster ce champ dans votre backend
        }

        response = requests.post(f"{API_BASE_URL}/employees/", data=data)

        if response.status_code == 201:
            self.main_window.info_dialog("Succès", f"Employé {name} ajouté avec succès.")
        else:
            print(f"Erreur {response.status_code}: {response.text}")  # Affiche la réponse du serveur pour déboguer
            self.main_window.error_dialog("Erreur", f"Impossible d'ajouter l'employé. Détails : {response.text}")
        self.show_add_employee_screen()  # Retour à l'accueil après ajout

    def show_employee_list(self, widget):
        """Affiche la liste des employés avec options de suppression et génération de badge PDF"""
        self.main_box.clear()
        self.create_employee_list_menu()
        response = requests.get(f"{API_BASE_URL}/employees/")
        if response.status_code == 200:
            employees = response.json()

            employee_table = toga.Table(
                        headings=["Nom", "Prénom", "Matricule", "Département", "Poste"],
                        style=Pack(flex=1, padding=10),

            )
            # Afficher la liste des employés
            for employee in employees:

                # Ligne avec données et boutons d'action
                employee_table.data.append([
                    employee["name"],
                    employee["firstname"],  # Prénom
                    employee["matricule"],   # Matricule
                    employee["departement"],  # Département
                    employee["position"]
                ])
                self.employees_list = employees
                self.main_box.add(employee_table)

        else:
            self.main_window.error_dialog("Erreur", f"Impossible de récupérer les employés. Détails : {response.text}")

        back_button = toga.Button("Retour", on_press=self.create_home_screen)
        self.main_box.add(back_button)

    def create_employee_list_menu(self):
        """Créer une barre de menu pour la liste des employés avec les options de suppression et génération de badge"""
        self.clear_menu_bar()  # Effacer le menu existant pour éviter les doublons

        # Commande pour supprimer un employé
        delete_cmd = toga.Command(
            self.show_delete_dialog,
            text="Supprimer",
            tooltip="Supprimer un employé",
            icon=toga.Icon('/Users/cbrian/Desktop/Attendance/attendance_app/frontend/PresenceApp/src/PresenceApp/garbage.png')
        )

        # Commande pour générer un badge
        badge_cmd = toga.Command(
            self.show_badge_dialog,
            text="Générer Badge",
            tooltip="Générer un badge pour un employé",
            icon=toga.Icon('/Users/cbrian/Desktop/Attendance/attendance_app/frontend/PresenceApp/src/PresenceApp/pdf-file.png')
        )

    # Commande pour modifier un employé
        modify_cmd = toga.Command(
            self.show_modify_dialog,
            text="Modifier",
            tooltip="Modifier les informations d'un employé",
            icon=toga.Icon('/Users/cbrian/Desktop/Attendance/attendance_app/frontend/PresenceApp/src/PresenceApp/edit_profile.png')
        )
        # Ajouter les commandes au menu de la fenêtre principale
        self.main_window.toolbar.add(delete_cmd)
        self.main_window.toolbar.add(badge_cmd)
        self.main_window.toolbar.add(modify_cmd)


    def show_delete_dialog(self, widget):
        """Afficher la boîte de dialogue pour la suppression d'un employé."""
        employee_matricules = [emp['matricule'] for emp in self.employees_list]  # Liste des noms d'employés
        self.employee_select = toga.Selection(items=employee_matricules)

        submit_button = toga.Button("Confirmer la suppression", on_press=self.confirm_delete)
        cancel_button = toga.Button("Annuler", on_press=self.close_dialog)

        # Créer une boîte pour les boutons
        buttons_box = toga.Box(style=Pack(direction=ROW, padding=5))
        buttons_box.add(submit_button)
        buttons_box.add(cancel_button)

        # Créer la boîte de dialogue
        self.dialog_box = toga.Box(style=Pack(direction=COLUMN, padding=10, width=70))
        self.dialog_box.add(self.employee_select)
        self.dialog_box.add(buttons_box)

        # Afficher la boîte de dialogue
        self.main_box.add(self.dialog_box)

    def confirm_delete(self, widget):
        """Confirmer la suppression de l'employé sélectionné."""
        selected_employee = self.employee_select.value
        if selected_employee:
            employee = next((emp for emp in self.employees_list if emp["matricule"] == selected_employee), None)
            if employee:
                self.delete_employee(employee["id"])
                self.main_box.remove(self.dialog_box)  # Fermer la boîte de dialogue
                self.show_employee_list()  # Mettre à jour l'affichage des employés

    def show_badge_dialog(self, widget):
        """Afficher la boîte de dialogue pour générer un badge pour un employé."""
        employee_matricules = [emp['matricule'] for emp in self.employees_list]  # Liste des noms d'employés
        self.employee_select = toga.Selection(items=employee_matricules)

        submit_button = toga.Button("Générer Badge", on_press=self.confirm_generate_badge)
        cancel_button = toga.Button("Annuler", on_press=self.close_dialog)

        # Créer une boîte pour les boutons
        buttons_box = toga.Box(style=Pack(direction=ROW, padding=5))
        buttons_box.add(submit_button)
        buttons_box.add(cancel_button)

        # Créer la boîte de dialogue
        self.dialog_box = toga.Box(style=Pack(direction=COLUMN, padding=10, width=70))
        self.dialog_box.add(self.employee_select)
        self.dialog_box.add(buttons_box)

        # Afficher la boîte de dialogue
        self.main_box.add(self.dialog_box)

    def confirm_generate_badge(self, widget):
        """Confirmer la génération du badge pour l'employé sélectionné."""
        selected_employee = self.employee_select.value
        if selected_employee:
            employee = next((emp for emp in self.employees_list if emp["matricule"] == selected_employee), None)
            if employee:
                self.generate_badge(employee)
                #self.main_box.remove(self.dialog_box)  # Fermer la boîte de dialogue

    def close_dialog(self, widget):
        """Fermer la boîte de dialogue."""
        if self.dialog_box in self.main_box.children:
            self.main_box.remove(self.dialog_box)  # Retirer la boîte de dialogue

    def delete_employee(self, employee_id):
        """Supprimer un employé via l'API backend"""
        response = requests.delete(f"{API_BASE_URL}/employees/{employee_id}/")
        if response.status_code == 204:
            self.main_window.info_dialog("Succès", "Employé supprimé avec succès.")
        else:
            self.main_window.error_dialog("Erreur", f"Impossible de supprimer l'employé. Détails : {response.text}")

        self.show_employee_list(None)  # Rafraîchir la liste après suppression

    def generate_badge(self, employee):
        """Générer un badge PDF avec le nom, le poste et un QR code généré à nouveau"""
        # Générer un QR code basé sur le nom et le poste de l'employé
        qr_data = f"Nom: {employee['name']}, Prénom: {employee['firstname']}, " \
                  f"Matricule: {employee['matricule']}, Poste: {employee['position']}, " \
                  f"Département: {employee['departement']}"
        qr_img = qrcode.make(qr_data)

        # Sauvegarder l'image QR dans un fichier temporaire
        temp_file = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
        qr_img.save(temp_file, format="PNG")
        temp_file.close()

        # Vérification de l'image avant de l'utiliser dans le PDF
        try:
            img = Image.open(temp_file.name)
            img.verify()  # Vérifie si l'image est valide
            img.close()   # Fermer après vérification
        except Exception as e:
            self.main_window.error_dialog("Erreur", f"Impossible de lire le fichier QR code. Détails : {e}")
            return

        # Créer un fichier PDF pour le badge
        pdf_file = f"{employee['name']}_badge.pdf"
        c = canvas.Canvas(pdf_file, pagesize=letter)
        width, height = letter

        employee_info1 = f"Nom: {employee['name']} | Prénom: {employee['firstname']} | Matricule: {employee['matricule']} "
        employee_info2 = f"| Poste: {employee['position']} | Département: {employee['departement']}"
        c.drawString(100, height - 100, employee_info1)
        c.drawString(100, height - 120, employee_info2)
        # Ajouter le QR code existant au PDF
        c.drawImage(temp_file.name, 100, height - 250, width=100, height=100)
        c.save()

        self.main_window.info_dialog("Succès", f"Badge généré pour {employee['name']} au format PDF.")

    def show_modify_dialog(self, widget):
        """Afficher une boîte de dialogue pour sélectionner l'employé à modifier."""
        employee_matricules = [emp['matricule'] for emp in self.employees_list]
        self.employee_select = toga.Selection(items=employee_matricules)

        submit_button = toga.Button("Modifier", on_press=self.open_modify_interface)
        cancel_button = toga.Button("Annuler", on_press=self.close_dialog)

        buttons_box = toga.Box(style=Pack(direction=ROW, padding=5))
        buttons_box.add(submit_button)
        buttons_box.add(cancel_button)

        self.dialog_box = toga.Box(style=Pack(direction=COLUMN, padding=10, width=70))
        self.dialog_box.add(self.employee_select)
        self.dialog_box.add(buttons_box)

        self.main_box.add(self.dialog_box)

    def open_modify_interface(self, widget):
        """Afficher une interface pour modifier les informations de l'employé sélectionné."""
        selected_employee = self.employee_select.value
        if selected_employee:
            employee = next((emp for emp in self.employees_list if emp["matricule"] == selected_employee), None)
            if employee:
                self.main_box.clear()

                self.name_input = toga.TextInput(value=employee['name'], placeholder="Nom")
                self.firstname_input = toga.TextInput(value=employee['firstname'], placeholder="Prénom")
                self.departement_input = toga.TextInput(value=employee['departement'], placeholder="Département")
                self.position_input = toga.TextInput(value=employee['position'], placeholder="Poste")
                self.matricule_input = toga.TextInput(value=employee['matricule'], placeholder="Matricule")

                submit_button = toga.Button("Enregistrer", on_press=lambda w: self.save_modified_employee(employee["id"]))
                cancel_button = toga.Button("Annuler", on_press=self.show_employee_list)

                self.main_box.add(toga.Label("Modifier les informations de l'employé", style=Pack(padding=10)))
                self.main_box.add(self.name_input)
                self.main_box.add(self.firstname_input)
                self.main_box.add(self.departement_input)
                self.main_box.add(self.position_input)
                self.main_box.add(self.matricule_input)
                self.main_box.add(submit_button)
                self.main_box.add(cancel_button)

    def save_modified_employee(self, employee_id):
        """Enregistrer les modifications apportées à un employé."""
        modified_data = {
            "name": self.name_input.value,
            "firstname": self.firstname_input.value,
            "departement": self.departement_input.value,
            "position": self.position_input.value,
            "matricule": self.matricule_input.value
        }

        response = requests.put(f"{API_BASE_URL}/employees/{employee_id}/", json=modified_data)
        if response.status_code == 200:
            self.main_window.info_dialog("Succès", "Employé modifié avec succès.")
            self.show_employee_list(None)
        else:
            self.main_window.error_dialog("Erreur", f"Impossible de modifier l'employé. Détails : {response.text}")

        self.show_employee_list()
    #def start_qr_scanner(self, widget):
       # """Lancer le scanner de QR code via un Intent Android"""
        #print(f"platform.system(): {platform.system()}")
        #if platform.system() == "Linux":
            #try:
                #Intent = JavaClass('android.content.Intent')
                #scan_intent = Intent("com.google.zxing.client.android.SCAN")
                #activity = self._impl.native
                #print("Intent pour le scanner lancé avec requestCode 0.")
                #activity.startActivityForResult(scan_intent, 0)
                #self.main_window.on_activity_result = self.handle_qr_scan_result
            #except Exception as e:
                #self.main_window.error_dialog("Erreur", f"Impossible de lancer le scanner de QR code. Détails : {e}")
        #else:
            #self.main_window.error_dialog("Erreur", "Cette fonctionnalité est uniquement disponible sur Android.")

    #def handle_qr_scan_result(self, requestCode, resultCode, data):
        #"""Gestion directe du retour de l'Intent pour le scan QR"""
        #if requestCode == 0 and resultCode == -1:
            #print("Résultat du scan QR code reçu")
            #try:
                #extras = data.getExtras()
                #if extras is not None:
                    #qr_code_data = extras.getString("SCAN_RESULT")
                    #print(f"QR Code scanné: {qr_code_data}")
                    #if qr_code_data:
                        #now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        #self.display_employee_scan(qr_code_data, now)
                    #else:
                        #print("Aucun QR code trouvé dans l'intent.")
                #else:
                    #print("Pas d'extras dans l'intent.")
            #except Exception as e:
                #print(f"Erreur lors du traitement des données: {e}")
                #self.main_window.error_dialog("Erreur", f"Impossible de récupérer les données du QR code. Détails : {e}")
        #elif resultCode == 0:
            #print("Le scan a été annulé.")
            #self.main_window.info_dialog("Annulé", "Le scan a été annulé.")
        #else:
            #print(f"Aucun résultat correspondant pour requestCode={requestCode}")
    def create_presence_qr_folder(self):
        """Créer un dossier appelé 'PresenceQR' dans le stockage interne si nécessaire"""
        # Obtenir le chemin du dossier spécifique à l'application
        activity = self._impl.native  # Utiliser l'instance d'activité actuelle
        file = activity.getExternalFilesDir(None)  # répertoire pour les images
        folder_path = os.path.join(str(file.getAbsolutePath()), 'PresenceQR')  # Convertir en chaîne de caractères

        if not os.path.exists(folder_path):
            os.makedirs(folder_path)  # Créer le dossier s'il n'existe pas
            print(f"Dossier 'PresenceQR' créé : {folder_path}")
        else:
            print(f"Dossier 'PresenceQR' déjà existant : {folder_path}")

        return folder_path


    def capture_qr_code(self, widget):
        """Capturer une image avec la caméra pour analyse via ZXing"""
        self.request_permissions()
        try:
            folder_path = self.create_presence_qr_folder()

            image_name = f"qr_code_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
            # Capture une image avec la caméra et stocker l'image
            image_path = os.path.join(folder_path, image_name)
            camera.take_picture(filename=image_path, on_complete=self.on_picture_captured)
            print(f"Image capturée et enregistrée à : {image_path}")

            # Une fois l'image capturée, lancer ZXing pour analyser l'image
            self.analyze_qr_code_with_zxing(image_path)

        except Exception as e:
            self.main_window.error_dialog("Erreur", f"Cette fonctionnalité est uniquement disponible sur Android. : {e}")

    def on_picture_captured(self, image_path):
        """Callback lorsque l'image est capturée, et analyse le QR code"""
        print(f"Image capturée à : {image_path}")
        self.analyze_qr_code_with_zxing(image_path)

    def analyze_qr_code_with_zxing(self, image_path):
        """Analyser le QR code dans l'image capturée avec ZXing"""
        try:
            # Initialiser le scanner ZXing
            reader = zxing.BarCodeReader()

            # Scanner l'image contenant le QR code
            barcode = reader.decode(image_path)

            if barcode:
                qr_code_data = barcode.parsed
                print(f"QR Code détecté: {qr_code_data}")

                # Obtenir l'heure actuelle
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Afficher et traiter le scan du QR code
                self.display_employee_scan(qr_code_data, now)
            else:
                self.main_window.error_dialog("Erreur", "Aucun QR code détecté.")
        except Exception as e:
            self.main_window.error_dialog("Erreur", f"Échec du scan du QR code. Détails : {e}")
    def display_employee_scan(self, qr_code_data, now):
        """Afficher les informations scannées de l'employé avec date et heure, et option d'enregistrement"""
        self.main_box.clear()

        name_label = toga.Label(f"Nom: {qr_code_data}")
        datetime_label = toga.Label(f"Date et heure du scan: {now}")

        save_button = toga.Button("Enregistrer la présence", on_press=lambda w: self.save_attendance(qr_code_data, now))
        back_button = toga.Button("Retour", on_press=self.create_home_screen)

        self.main_box.add(name_label)
        self.main_box.add(datetime_label)
        self.main_box.add(save_button)
        self.main_box.add(back_button)
    def save_attendance(self, qr_code_data, now):
        """Enregistrer la présence de l'employé avec la date et l'heure via l'API"""
        # Rechercher l'employé dans le backend en fonction des données scannées (nom ou autre info)
        search_params = {'search': qr_code_data}
        employee_response = requests.get(f"{API_BASE_URL}/employees/", params=search_params)
        if employee_response.status_code == 200:
            employees = employee_response.json()

            if employees:
                # Si un employé est trouvé, utiliser son ID pour l'enregistrement de la présence
                employee = employees[0]  # Supposons que le premier résultat soit le bon
                employee_id = employee['id']

                attendance_data = {
                    "employee_id": employee_id,
                    "datetime": now
                }

                # Enregistrer la présence
                response = requests.post(f"{API_BASE_URL}/attendances/", json=attendance_data)

                if response.status_code == 201:
                    self.main_window.info_dialog("Succès", f"Présence de {employee['name']} enregistrée.")
                    self.create_home_screen()  # Retour à l'écran d'accueil après enregistrement
                else:
                    self.main_window.error_dialog("Erreur", f"Impossible d'enregistrer la présence. Détails : {response.text}")
            else:
                self.main_window.error_dialog("Erreur", "Aucun employé correspondant trouvé.")
        else:
            self.main_window.error_dialog("Erreur", f"Impossible de rechercher l'employé. Détails : {employee_response.text}")

    def refresh_presence_table(self, widget=None):
        """Rafraîchir le contenu du tableau de présences."""
        # Effacer les anciennes données du tableau
        self.main_box.clear()

        # Recréer l'interface pour afficher les présences
        self.view_presences(widget=None)

    def create_presence_list_menu(self):
        """Créer une barre de menu spécifique pour la liste des présences avec Ajouter Manuellement et Exporter en Excel"""
        self.clear_menu_bar()  # Supprimer tout menu existant pour éviter les doublons

        # Commande pour ajouter une présence manuellement
        add_manual_cmd = toga.Command(
            self.add_manual_presence,
            text="Ajouter Manuellement",
            tooltip="Ajouter une présence manuellement",
            icon=toga.Icon('/Users/cbrian/Desktop/Attendance/attendance_app/frontend/PresenceApp/src/PresenceApp/add.png')
        )

        # Commande pour exporter la liste des présences en Excel
        export_cmd = toga.Command(
            self.export_to_excel,
            text="Exporter en Excel",
            tooltip="Exporter la liste des présences au format Excel",
            icon=toga.Icon('/Users/cbrian/Desktop/Attendance/attendance_app/frontend/PresenceApp/src/PresenceApp/xls-file.png')
        )
        # Commande pour rafraîchir la liste des présences
        refresh_cmd = toga.Command(
            self.refresh_presence_table,
            text="Rafraîchir",
            tooltip="Rafraîchir la liste des présences",
            icon=toga.Icon('/Users/cbrian/Desktop/Attendance/attendance_app/frontend/PresenceApp/src/PresenceApp/refresh-data.png')  # Remplacez par le chemin de votre icône de rafraîchissement
        )
        # Ajouter les commandes spécifiques à la barre de menu
        self.main_window.toolbar.add(add_manual_cmd)
        self.main_window.toolbar.add(export_cmd)
        self.main_window.toolbar.add(refresh_cmd)

    def format_date(self, date_str):
        """Formater la date d'entrée sous une forme lisible avec conversion de l'heure UTC à l'heure locale de Madagascar"""
        try:
            # Convertir la chaîne de date en un objet datetime en UTC
            date_obj = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%fZ")
            date_obj = date_obj.replace(tzinfo=pytz.UTC)  # Indiquer que la date est en UTC

            # Convertir l'heure UTC en heure locale (Madagascar)
            local_tz = pytz.timezone("Indian/Antananarivo")
            local_time = date_obj.astimezone(local_tz)

            # Formater la date selon le format désiré
            return local_time.strftime("%d %B %Y, %H:%M")
        except ValueError:
            print(f"Erreur: Format de date incorrect pour {date_str}")
            return date_str
    def view_presences(self, widget):
        """Afficher la liste des présences enregistrées avec options d'ajout manuel et export en Excel"""
        self.main_box.clear()
        self.create_presence_list_menu()
        today_date = date.today().strftime('%Y-%m-%d')
        # Titre de l'interface
        title = toga.Label(f"Liste des présences pour le {today_date}", style=Pack(padding=10))
        self.main_box.add(title)

        # Récupérer la liste des employés pour lier les IDs des présences aux noms et postes
        employee_response = requests.get(f"{API_BASE_URL}/employees/")
        if employee_response.status_code == 200:
            employees = employee_response.json()
            # Créer un dictionnaire pour accéder rapidement aux employés par leur ID
            employee_dict = {emp['id']: emp for emp in employees}

            # Récupérer les présences depuis l'API
            attendance_response = requests.get(f"{API_BASE_URL}/attendances/")
            if attendance_response.status_code == 200:
                presences = attendance_response.json()

                # Créer un tableau pour afficher les présences
                presence_table = toga.Table(
                    headings=["Nom", "Prénom", "Matricule", "Département", "Poste", "Date/Heure d'entrée", "Date/Heure de sortie"],
                    style=Pack(flex=1, padding=10)
                )


                # Créer un dictionnaire pour stocker les entrées non associées à une sortie
                pending_entries = {}

                # Ajouter les données au tableau
                for presence in presences:
                    presence_date = presence.get("date", "")[:10]  # Extraire "YYYY-MM-DD" en utilisant les 10 premiers caractères
                    if presence_date != today_date:
                        continue
                    employee_id = presence['employee_id']
                    employee = employee_dict.get(employee_id)

                    if employee:
                        
                        name = employee["name"]
                        firstname = employee["firstname"]
                        matricule = employee["matricule"]
                        departement = employee["departement"]
                        position = employee["position"]
                    else:
                        name = "Employé inconnu"
                        firstname = "Inconnu"
                        matricule = "Non disponible"
                        departement = "Non disponible"
                        position = "Inconnu"

                    # Initialisation des temps d'entrée et de sortie
                    entry_time = None
                    exit_time = None

                    # Si la présence est de type "entrée"
                    if presence['type'] == "entrée":
                        entry_time = presence.get("date")  # La date/heure d'entrée
                        # Stocker l'entrée dans le dictionnaire en attendant la sortie
                        pending_entries[employee_id] = {"entry_time": entry_time, "exit_time": None}
                    # Si la présence est de type "sortie"
                    elif presence['type'] == "sortie":
                        exit_time = presence.get("date")  # La date/heure de sortie
                        # Chercher l'entrée correspondante
                        if employee_id in pending_entries:
                            pending_entries[employee_id]["exit_time"] = exit_time

                    # Si un employé a une entrée sans sortie, on doit ajouter son entrée dans le tableau
                    if employee_id in pending_entries:
                        pending_entry = pending_entries[employee_id]
                        # Formater les dates d'entrée et de sortie avec la fonction format_date
                        formatted_entry_time = self.format_date(pending_entry["entry_time"]) if pending_entry["entry_time"] else "Non défini"
                        formatted_exit_time = self.format_date(pending_entry["exit_time"]) if pending_entry["exit_time"] else "Non défini"

                        # Ajouter une ligne pour l'entrée, avec la sortie si disponible
                        presence_table.data.append([name, firstname, matricule, departement, position, formatted_entry_time, formatted_exit_time])



                # Ajouter le tableau à l'interface
                self.main_box.add(presence_table)
            else:
                self.main_window.error_dialog("Erreur", f"Impossible de récupérer les présences. Détails : {attendance_response.text}")
        else:
            self.main_window.error_dialog("Erreur", f"Impossible de récupérer les employés. Détails : {employee_response.text}")

        back_button = toga.Button("Retour", on_press=self.create_home_screen)
        self.main_box.add(back_button)


    def update_employee_list(self):
        """Mettre à jour la liste locale des employés depuis l'API"""
        response = requests.get(f"{API_BASE_URL}/employees/")
        if response.status_code == 200:
            self.employees = response.json()
            print(f"Employés récupérés : {self.employees}")  # Débogage

        else:
            self.main_window.error_dialog("Erreur", f"Impossible de récupérer les employés. Détails : {response.text}")

    def add_manual_presence(self, widget):
        """Ajouter manuellement une présence avec les mêmes informations que lors du scan QR code"""
        self.main_box.clear()

        # Sélectionner un employé existant par matricule
        self.update_employee_list()
        employee_matricules = [emp['matricule'] for emp in self.employees]
        print(f"Matricules des employés pour la sélection : {employee_matricules}")  # Débogage
        self.employee_select = toga.Selection(items=employee_matricules)

        submit_button = toga.Button("Ajouter Présence", on_press=self.save_manual_presence)
        back_button = toga.Button("Retour", on_press=self.view_presences)

        self.main_box.add(toga.Label("Sélectionner un matricule d'employé", style=Pack(padding=10)))
        self.main_box.add(self.employee_select)
        self.main_box.add(submit_button)
        self.main_box.add(back_button)


    def save_manual_presence(self, widget):
        """Enregistrer une présence manuelle avec la date et l'heure actuelles"""
        selected_matricule = self.employee_select.value
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%d %H:%M:%S")

        if selected_matricule:
            # Trouver l'employé correspondant au matricule sélectionné
            employee = next((emp for emp in self.employees if emp['matricule'] == selected_matricule), None)
            if employee:
                # Envoyer une demande de création de présence sans vérifier l'historique
                attendance_data = {
                    "employee_id": employee['id'],
                    "date": date_time,  # Optionnel si l'API utilise automatiquement la date actuelle
                }
                response = requests.post(f"{API_BASE_URL}/attendances/", json=attendance_data)

                # Vérifier le statut de la réponse
                if response.status_code == 201:
                    # Afficher un message de succès
                    self.main_window.info_dialog("Succès", f"Entrée de {employee['matricule']} enregistrée.")
                else:
                    # Afficher un message d'erreur en cas d'échec
                    self.main_window.info_dialog("Succès", f"Sortie de {employee['matricule']} enregistrée.")
            else:
                self.main_window.error_dialog("Erreur", "Employé non trouvé.")
        else:
            self.main_window.error_dialog("Erreur", "Veuillez sélectionner un matricule d'employé.")

        self.view_presences(widget)


    def export_to_excel(self, widget):
        """Exporter la liste des présences au format Excel pour la date actuelle"""
        from datetime import datetime

        # Récupérer la date du jour
        today_date = datetime.now().strftime('%Y-%m-%d')

        # Récupérer la liste des employés pour la correspondance avec l'employee_id
        employee_response = requests.get(f"{API_BASE_URL}/employees/")
        if employee_response.status_code == 200:
            employees = employee_response.json()
            # Créer un dictionnaire pour accéder rapidement aux employés par leur ID
            employee_dict = {emp['id']: emp for emp in employees}

            # Récupérer les présences depuis l'API
            attendance_response = requests.get(f"{API_BASE_URL}/attendances/")
            if attendance_response.status_code == 200:
                presences = attendance_response.json()

                # Créer un dictionnaire pour regrouper les entrées et sorties
                pending_entries = {}

                # Préparer les données pour l'exportation
                data = []
                for presence in presences:
                    presence_date = presence.get("date", "")[:10]  # Extraire "YYYY-MM-DD" à partir de la date complète
                    if presence_date != today_date:  # Filtrer les données pour la date actuelle
                        continue

                    employee_id = presence['employee_id']
                    employee = employee_dict.get(employee_id)

                    if employee:
                        name = employee["name"]
                        firstname = employee["firstname"]
                        matricule = employee["matricule"]
                        departement = employee["departement"]
                        position = employee["position"]
                    else:
                        name = "Employé inconnu"
                        firstname = "Inconnu"
                        matricule = "Non disponible"
                        departement = "Non disponible"
                        position = "Inconnu"

                    # Gérer les types de présences
                    if presence['type'] == "entrée":
                        entry_time = presence.get("date")
                        pending_entries[employee_id] = {"entry_time": entry_time, "exit_time": None}
                    elif presence['type'] == "sortie":
                        exit_time = presence.get("date")
                        if employee_id in pending_entries:
                            pending_entries[employee_id]["exit_time"] = exit_time

                # Créer les lignes de données pour l'export
                for employee_id, times in pending_entries.items():
                    entry_time = times["entry_time"]
                    exit_time = times["exit_time"]
                    data.append({
                        "Nom": employee_dict.get(employee_id, {}).get("name", "Employé inconnu"),
                        "Prénom": employee_dict.get(employee_id, {}).get("firstname", "Inconnu"),
                        "Matricule": employee_dict.get(employee_id, {}).get("matricule", "Non disponible"),
                        "Département": employee_dict.get(employee_id, {}).get("departement", "Non disponible"),
                        "Poste": employee_dict.get(employee_id, {}).get("position", "Inconnu"),
                        "Date/Heure d'entrée": self.format_date(entry_time) if entry_time else "Non défini",
                        "Date/Heure de sortie": self.format_date(exit_time) if exit_time else "Non défini",
                    })

                # Créer un DataFrame et l'exporter en Excel
                df = pd.DataFrame(data)
                export_filename = f"presences_{today_date}.xlsx"  # Nom du fichier avec la date
                df.to_excel(export_filename, index=False)

                self.main_window.info_dialog("Succès", f"La liste des présences a été exportée avec succès en Excel : {export_filename}")
            else:
                self.main_window.error_dialog("Erreur", f"Impossible de récupérer les présences. Détails : {attendance_response.text}")
        else:
            self.main_window.error_dialog("Erreur", f"Impossible de récupérer les employés. Détails : {employee_response.text}")




def main():
    return AttendanceApp()

if __name__ == '__main__':
    main().main_loop()
