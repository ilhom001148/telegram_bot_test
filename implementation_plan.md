# [1-Darajali Yangilanishlar o'rnatilishi]

Bu reja Telegram botingiz ichiga siz tanlagan 3 ta ajoyib Premium funksiyalarni qo'shish jarayonini tushuntirib beradi. 

## Proposed Changes

### 1. "Xabar yuborish" ni rejalashtirish (Scheduled Broadcast)
Mavjud xabar yuborish bo'limiga **"Taymer o'rnatish"** xususiyati kiritiladi.

#### [MODIFY] `bot/models.py`
Yangi Jadval (Table) kiritamiz: `ScheduledBroadcast`. Bu jadval o'z ichiga qaysi xabar, qachon yuborilishi va kimga (barchagami yoki alohida guruhgami) ketishini saqlaydi.

#### [MODIFY] `bot/main.py`
Botning orqa fonida ishlaydigan `broadcast_scheduler_worker()` funksiyasini yozamiz. U har minutda bazani tekshirib, agar vaqti kelgan e'lon bo'lsa, foydalanuvchilar va guruhlarga yuboradi, va muvaffaqiyatli jo'natilganligini bazaga qayd qilib qoyadi.

#### [MODIFY] `admin-panel/src/App.jsx`
`BroadcastManager` interfeysiga "Qachon yuborilsin?" degan tugma va vaqt tanlovchi (Datetime picker) kiritiladi. Hozir bevosita jo'natilish o'rniga, sanani saqlab qo'yish ruxsati beriladi.

---

### 2. Ma'lumotlarni Yuklab Olish (Export to Excel/CSV)
Har qanday biznes uchun o'qitilgan bilimlar (Q&A) va mijozlarning eng ko'p so'ragan savollarini Excel faylda yuklash kerak.

#### [NEW] `api/routes/export.py`
Maxsus API. Bu backend URL orqali siz bitta tugmani bosganda orqa devorda SQL bazasidagi jadvalli ma'lumotlar .csv (Excel) formatiga o'zgirilib tayyorlanadi va to'g'ridan to'g'ri brauzeringizga yuklanadi.

#### [MODIFY] `api/main.py`
Ushbu yangi routeni tizimning markaziga bog'laymiz.

#### [MODIFY] `admin-panel/src/App.jsx`
Tegishli joylarda (masalan: O'qitish bo'limi va Muloqotlar bo'limida) chiroyi oq/yashil "📥 Excelda yuklab olish" tugmalarini qo'shamiz. Bitta bosganingizda joriy ma'lumotlar kompyuteringizda tushadi.

---

### 3. CRM Modeli - Faol Mijozlar ro'yxati (User Profiling)
Mijozlarni kim guruhdan nimalar so'rayotganini alohida shaxsiylashgan holda ko'rish.

#### [NEW] `api/routes/users.py`
CRM kabi ishlaydigan backend qismi. Bu API botga umrida bir marta bo'lsa ham yozgan insonlarning ma'lumotlarini hisoblab: Kim? Nechta xabar yozgan? Nechta savolli xabar bergan? Kabi analizlarni hisob-kitob qiladi.

#### [MODIFY] `admin-panel/src/App.jsx`
Admin paneldagi chap taraf yon menyusiga yupang-yangi **"👥 Mijozlar (CRM)"** yorlig'ini qo'shamiz (Guruhlar tagida). Bu oyna sizga aynan foydalanuvchilar qatlamini tartib bilan kuzatish, ular bilan tanishish imkoniyatini beradi.

## User Review Required

> [!WARNING]
> Tizim xabarlarni taymer(vaqt) bilan yuborishi uchun sizga "Botni qayta yoqish" (Restart) hamda bazaga yangi jadval (Table) qo'shayotganligimiz sabab, ma'lumotlar bazasi structurasi yangilanadi. Bu sizning hozirgi yozishmalaringiz va bilimlar ro'yxatiga zarracha zarar qilmaydi, lekin xabardor qilib qoyish zimmamda. 
> 
> **Tasdiqlaysizmi? Ishni boshlashim mumkinmi?**
