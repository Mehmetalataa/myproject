import sqlite3
import http.client
import json
import urllib.request
from tkinter import *
from tkinter import messagebox, simpledialog
from PIL import Image, ImageTk

API_KEY = "b20bde7"
film= None


baglanti = sqlite3.connect("movies.db")
baglanti.execute("CREATE TABLE IF NOT EXISTS Filmler(Title, Yil, Tur, Oyuncular, Imdb, Konu)")
baglanti.execute("CREATE TABLE IF NOT EXISTS Yorumlar(Title, Yorum)")
baglanti.commit()

                 
def filmismi():       
    global film
    try:     #bazı filmlerde hata alıyordum o hatayı chatgpt'ye düzelttirdim.(görsel1.1,görsel1.2)
        baslik = inputAra.get().strip()
        if not baslik:
            messagebox.showwarning("Uyarı", "Lütfen bir film adı giriniz.")
            return
        from urllib.parse import quote
        baslik_encoded = quote(baslik)

        conn = http.client.HTTPSConnection("www.omdbapi.com")  #chatgpt yardımı alındı.(görsel2)
        conn.request("GET", "/?apikey=" + API_KEY + "&t=" + baslik_encoded, {})
        res = conn.getresponse()
        f = json.loads(res.read())
        if f.get("Response") == "True":
            film = f
            lblBaslik.config(text=f["Title"] + " (" + f["Year"] + ")")
            lbveri.delete(0, END)
            lbveri.insert(END, "Yıl: " + f.get("Year",""))
            lbveri.insert(END, "Tür: " + f.get("Genre",""))
            lbveri.insert(END, "Oyuncular: " + f.get("Actors",""))
            lbveri.insert(END, "IMDb: " + f.get("imdbRating",""))
            lbveri.insert(END, f.get("Plot",""))
            poster = f.get("Poster")
            if poster and poster != "N/A":
                u = urllib.request.urlopen(poster)
                im = Image.open(u).resize((180,270))
                img = ImageTk.PhotoImage(im)
                lblResim.config(image=img, text="", width=180, height=270)
                lblResim.image = img
            else:
                lblResim.config(text="Poster yok", image="", width=20, height=13)
        else:
            messagebox.showwarning("HATA", "Film bulunamadı")
    except Exception as e:
        messagebox.showerror("Hata", f"Bir hata oluştu:\n{e}")


def kaydet():
    if film:
        baglanti.execute(
            "INSERT OR IGNORE INTO Filmler VALUES(?,?,?,?,?,?)",  #chatgpt yardımı alındı.(görsel3) 
            [film["Title"], film["Year"], film["Genre"],
             film["Actors"], film["imdbRating"], film["Plot"]]
        )
        y = yorumAlani.get("1.0", END).strip()
        if y:
            baglanti.execute("INSERT INTO Yorumlar VALUES(?,?)",
                             [film["Title"], y])
            yorumAlani.delete("1.0", END)
        baglanti.commit()
    else:
        messagebox.showwarning("HATA", "Kaydedilecek film yok")

def KayitlariGoster():
    pencere2 = Toplevel()
    pencere2.title("Kayıtlı Filmler")
    pencere2.geometry("500x400")
    pencere2.config(bg="#F1F8E9")

    Label(pencere2, text="Kayıtlı Filmler", font=("Arial", 16, "bold"), bg="#F1F8E9").pack(pady=10)

    lbKayitli = Listbox(pencere2, font=("Arial", 11), width=60, height=20, bg="#E3F2FD")
    lbKayitli.pack(pady=10)

    for k in baglanti.execute("SELECT Title, Yil, Tur FROM Filmler"):
        lbKayitli.insert(END, f"{k[0]} ({k[1]}) - {k[2]}")

def YorumlariGoster():
    lbYorumlar.delete(0, END)
    for k in baglanti.execute("SELECT Title, Yorum FROM Yorumlar"):
        lbYorumlar.insert(END, k[0] + " : " + k[1])

#arayüz tasarımında youtubeden öğrendiğim bilgileri kullandım.
#https://www.youtube.com/watch?v=ioNfInaP-EA&list=PLSmHiN0iazy_qX_6Tmecj4tTOefqh2-m2&pp=0gcJCV8EOCosWNin
pencere = Tk()
pencere.geometry("750x800")
pencere.title("Filmpal")
pencere.config(bg="#E8F6EF")

Label(pencere, text="Film Bilgileri", font=("Arial", 20, "bold"), bg="#E8F6EF").pack(pady=10)

inputAra = Entry(pencere, font=("Arial", 14), justify="center")
inputAra.pack(pady=10)

Button(pencere, text="Ara", font=("Arial", 13), bg="#FFA55D", fg="white", command=filmismi).pack(pady=6)
Button(pencere, text="Kaydet", font=("Arial", 13), bg="#2196F3", fg="white", command=kaydet).pack(pady=6)
Button(pencere, text="Kayıtlıları Göster", font=("Arial", 13), bg="#3D365C", fg="white", command=KayitlariGoster).pack(pady=6)

Label(pencere, text="Senin Yorumun (isteğe bağlı)", bg="#E8F6EF", font=("Arial", 12)).pack(pady=4)
yorumAlani = Text(pencere, height=4, width=50, font=("Arial", 11))
yorumAlani.pack(pady=5)

lblResim = Label(pencere, bg="#E8F6EF", text="")
lblResim.pack(pady=10)

lblBaslik = Label(pencere, text="", font=("Arial", 16, "bold"), bg="#E8F6EF")
lblBaslik.pack(pady=5)

lbveri = Listbox(pencere, font=("Arial", 11), width=60, height=6, bg="#F0FFFF")
lbveri.pack(pady=10)


lbYorumlar = Listbox()  

pencere.mainloop()
