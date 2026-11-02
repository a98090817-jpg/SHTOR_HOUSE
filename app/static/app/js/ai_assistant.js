(function () {
  const root = document.querySelector('[data-curtain-assistant]');
  if (!root) return;

  const toggle = root.querySelector('[data-assistant-toggle]');
  const panel = root.querySelector('[data-assistant-panel]');
  const closeButton = root.querySelector('[data-assistant-close]');
  const form = root.querySelector('[data-assistant-form]');
  const input = root.querySelector('[data-assistant-input]');
  const sendButton = root.querySelector('[data-assistant-send]');
  const messages = root.querySelector('[data-assistant-messages]');
  const suggestions = root.querySelector('[data-assistant-suggestions]');
  const status = root.querySelector('[data-assistant-status]');
  const languageSelect = document.getElementById('language-select');
  const conversation = [];
  let closeTimer;

  const copyByLanguage = {
    uz: {
      chatOpen: 'Maslahat',
      chatTitle: 'Parda maslahatchisi',
      chatOnline: 'Sizga yordam berishga tayyor',
      chatClose: 'Chatni yopish',
      chatWelcome: 'Assalomu alaykum! Men klassik pardalar, tyul, blackout, rolikli va zebra pardalar, rim pardalari hamda gorizontal/vertikal jalyuzilar bo‘yicha maslahat beraman. Qaysi turi haqida bilmoqchisiz?',
      chatQuestionMaterials: 'Parda turlari',
      chatQuestionMeasure: 'Jalyuzi turlari',
      chatQuestionPrice: 'Narx va o‘lcham',
      chatGreeting: 'Assalomu alaykum! Parda, tyul, jalyuzi, mato, o‘lcham, parvarish yoki narx haqida bemalol so‘rang. Qaysi xona uchun parda tanlayapsiz?',
      chatTypes: 'Asosiy turlar: klassik ikki qatlamli parda (tyul + qalin parda), blackout yoki dimout, lyuversli (halqali), lenta bilan burmali va wave uslubidagi parda. Ko‘tariladigan turlarga rolikli, zebra (kun-tun) va rim pardalari kiradi; jalyuzilarda gorizontal, vertikal va yog‘och lamelli variantlar bor. Katta oynalar uchun panel/yapon pardasi, maxsus ko‘rinish uchun lambreken yoki dekorativ yon pardalar tanlanadi. Tanlov xona, deraza o‘lchami, yorug‘lik va parvarish talabiga bog‘liq.',
      chatPlaceholder: 'Savolingizni yozing...',
      chatInputLabel: 'Xabaringiz',
      chatSend: 'Xabarni yuborish',
      chatMaterials: 'Parda uchun paxta (tabiiy va nafas oladi), zig‘ir (teksturali, tabiiy), ipak (nozik va nafis), baxmal (og‘irroq, yorug‘likni kamaytiradi), polyester (chidamli va parvarishi oson), shuningdek jacquard, atlas, organza va tyul ishlatiladi. Blackout mato yorug‘likni kuchli to‘sadi; dimout esa uni kamaytiradi, lekin odatda to‘liq qorong‘ilik bermaydi. Oshxona uchun yuvilishi oson mato, yotoqxona uchun astarli yoki blackout variantni ko‘rib chiqing. Matoning tarkibi va yuvish yorlig‘ini xariddan oldin tekshiring.',
      chatPanel: 'Panel yoki yapon pardasi keng tekis mato panellaridan iborat bo‘lib, rels bo‘ylab yon tomonga suriladi. Katta deraza, vitraj yoki xonani zonalarga ajratish uchun qulay; mato va panel soni rels kengligiga qarab belgilanadi. O‘rnatishdan oldin panel yig‘iladigan tomonda joy borligini tekshiring.',
      chatMotorized: 'Elektr yuritmali parda masofadan boshqariladi yoki aqlli uy tizimiga ulanadi; baland, katta yoki qiyin yetiladigan oynalarda qulay. Motor va karniz matoning og‘irligi hamda rels turiga mos tanlanadi, elektr ta’minoti va boshqaruv usuli oldindan rejalashtiriladi. Moslikni o‘rnatishdan oldin mutaxassis bilan tekshiring.',
      chatBlackout: 'Blackout — yorug‘likni juda kuchli to‘sadigan zich yoki maxsus qoplamali mato; yotoqxona, bolalar xonasi va kunduzgi uyqu uchun foydali. Yon chetlardan yorug‘lik kirishini kamaytirish uchun parda derazadan kengroq va balandroq osiladi yoki rolikli blackout tanlanadi. Dimout yorug‘likni kamaytiradi, lekin odatda xonani to‘liq qorong‘i qilmaydi.',
      chatInstall: 'Avval parda devor/karniz ustiga yoki rom ichiga o‘rnatilishini tanlang. Karnizni deraza kengligidan ikki tomonda yetarli chiqib turadigan qilib joylashtirish pardani ochganda oynani to‘sib qo‘ymaslikka yordam beradi; devor materiali va parda og‘irligiga mos kronshteyn hamda mahkamlagich kerak. Rolikli va jalyuzi mahsulotlarida ishlab chiqaruvchi bergan montaj sxemasi va o‘lcham qoidalariga amal qiling.',
      chatMeasure: 'Avval karniz yoki deraza kengligini, so‘ng karnizdan polgacha bo‘lgan balandlikni o‘lchang. Burmali klassik parda uchun mato eni odatda karniz kengligidan 1,5–2 baravar olinadi; tyulga ko‘proq burma berilishi mumkin. Rolikli, rim va ichki o‘rnatiladigan jalyuzilarda o‘lchash usuli boshqacha: rom ichiga o‘rnatishda oynaning ichki kengligi va balandligi bir necha nuqtadan o‘lchanadi. Buyurtmadan oldin o‘lcham va o‘rnatish turini mutaxassis bilan tasdiqlang.',
      chatPrice: 'Yakuniy narx mato turi va sarfi, karniz/deraza o‘lchami, tikuv modeli, furnitura hamda o‘rnatish xizmatiga qarab hisoblanadi. Katalogdagi narxlar mahsulotga tegishli bo‘lib, individual o‘lchamdagi buyurtma narxi farq qilishi mumkin. Aniq hisob uchun deraza kengligi-balandligi, xona va yoqtirgan turini yozing yoki +998 97 424 42 42 raqamiga qo‘ng‘iroq qiling.',
      chatBlinds: 'Jalyuzilarning asosiy turlari: gorizontal (alyuminiy yoki yog‘och lamelli), vertikal (mato lamelli), rolikli, zebra/kun-tun va rim pardalari. Gorizontal jalyuzi yorug‘likni lamellarni burab boshqaradi; vertikal turi keng deraza va ofisga mos. Rolikli parda matoni valga yig‘adi, zebra esa shaffof va zich yo‘llarni surib yorug‘likni sozlaydi; rim pardasi tepaga taxlam bo‘lib ko‘tariladi. Oshxona yoki nam joyda oson artiladigan material, yotoqxonada esa blackout matoli variantni ko‘rib chiqing.',
      chatRoller: 'Rolikli parda matoni yuqoridagi valga o‘raydi va derazani ixcham yopadi. Shaffof/light-filtering mato yorug‘likni yumshatadi, dimout uni ancha kamaytiradi, blackout esa xonani kuchli qorong‘ilatadi. Uni rom ichiga yoki devor/karniz ustiga o‘rnatish mumkin; ichki o‘rnatishda tutqich va rom chuqurligini ham hisobga oling.',
      chatZebra: 'Zebra yoki “kun-tun” parda shaffof va zich gorizontal yo‘lakli ikki qatlam matodan iborat. Qatlamlarni surib yo‘laklarni moslashtirasiz: yorug‘lik kiradi, yumshoq tarqaladi yoki ko‘proq to‘siladi. U ixcham va zamonaviy, lekin to‘liq qorong‘ilik kerak bo‘lsa alohida blackout matoni tanlang.',
      chatRoman: 'Rim pardasi ko‘tarilganda mato gorizontal taxlamlarga yig‘iladi; tushirilganda derazani tekis yopadi. Silliq, astarli yoki blackout matoli qilinadi va kichik derazalarda joyni tejaydi. O‘lchashda rom ichiga yoki tashqarisiga o‘rnatilishini oldindan belgilang.',
      chatHorizontal: 'Gorizontal jalyuzi alyuminiy, yog‘och yoki namlikka chidamli sun’iy yog‘och lamellardan tayyorlanadi. Lamellarni burab yorug‘lik va ko‘rinishni aniq boshqarish mumkin; alyuminiy yengil va amaliy, yog‘och esa iliqroq interyer ko‘rinishini beradi. Oshxonada yog‘och tanlashdan oldin namlik va parvarish talabini hisobga oling.',
      chatVertical: 'Vertikal jalyuzida uzun mato yoki boshqa material lamellari yon tomonga suriladi va o‘z o‘qi atrofida buriladi. Keng deraza, balkon eshigi va ofis oynalarini yopishga qulay. Lamella kengligi, yig‘ilish tomoni va deraza tutqichlariga tegmasligini o‘lchamdan oldin aniqlash kerak.',
      chatClassic: 'Klassik pardalar odatda tyul va zich yon pardadan tuziladi. Ularni parda lentasi bilan burmali, lyuvers (halqa) bilan, yashirin ilgakli yoki zamonaviy wave uslubida tikish mumkin. Burma ko‘rinishi uchun karniz eniga nisbatan mato koeffitsiyenti tanlanadi; karniz va mato og‘irligi bir-biriga mos bo‘lsin.',
      chatCleaning: 'Parvarish mato yorlig‘idagi ko‘rsatmaga bog‘liq: yuvishdan oldin ilgak va furniturani yeching, ranglarni ajrating, nozik rejim va past haroratdan foydalaning. Baxmal, ipak, qoplamali blackout va ayrim jalyuzilarni uyda yuvish matoni buzishi mumkin — quruq tozalash yoki ishlab chiqaruvchi ko‘rsatmasini tanlang. Changni muntazam yumshoq cho‘tka yoki changyutgichning past quvvatida oling.',
      chatChoose: 'Tanlashda 4 narsani hisobga oling: xona (yotoqxona/mehmonxona/oshxona), kerakli yorug‘lik va maxfiylik, deraza o‘lchami/o‘rnatish joyi, parvarish va budjet. Yotoqxonaga blackout yoki zich astarli parda, mehmonxonaga tyul va dekorativ yon parda, oshxonaga yengil yuviladigan rolikli yoki qisqa model mos kelishi mumkin. Derazangiz turi, xona va yorug‘lik istagingizni yozsangiz, mos variantlarni solishtirib beraman.',
      chatOffTopic: 'Kechirasiz, bu mavzu bo‘yicha ilmim yetmaydi. Men faqat parda, tyul, jalyuzi, mato tanlash, o‘lcham, o‘rnatish, parvarish va narx bo‘yicha yordam bera olaman. Shu mavzulardan birini so‘rang.',
      chatOrder: 'Buyurtma yoki individual maslahat uchun telefon qiling: +998 97 424 42 42. Mato turi va deraza o‘lchamlarini aytsangiz, mos variantni topishga yordam beramiz.',
      chatFallback: 'Savolingizni tushunmadim. Parda turi, mato, yorug‘likni to‘sish, jalyuzi, o‘lchash, o‘rnatish, parvarish yoki narxni aniqroq yozing.',
      chatError: 'Hozir javob olishda muammo yuz berdi. Birozdan so‘ng qayta urinib ko‘ring yoki +998 97 424 42 42 raqamiga qo‘ng‘iroq qiling.',
      chatWorking: 'Javob tayyorlanmoqda...'
    },
    en: {
      chatOpen: 'Ask us',
      chatTitle: 'Curtain advisor',
      chatOnline: 'Here to help you choose',
      chatClose: 'Close chat',
      chatWelcome: 'Hello! I can advise on drapes, sheers, blackout, roller and zebra blinds, Roman shades, and horizontal or vertical blinds. What would you like to know?',
      chatQuestionMaterials: 'Curtain types',
      chatQuestionMeasure: 'Blind types',
      chatQuestionPrice: 'Price & measuring',
      chatGreeting: 'Hello! Ask me about curtains, sheers, blinds, fabrics, measuring, care or pricing. Which room are you choosing for?',
      chatTypes: 'Common options include classic drapes with sheers, blackout or dimout curtains, eyelet, tape-pleated and wave styles. Compact options include roller shades, zebra/day-night blinds and Roman shades; blinds also come in horizontal, vertical and wood-slat designs. Panel/Japanese curtains work well for wide windows, while valances and side panels add decoration. The best choice depends on the room, window, light and care needs.',
      chatPlaceholder: 'Type your question...',
      chatInputLabel: 'Your message',
      chatSend: 'Send message',
      chatMaterials: 'Curtain fabrics include cotton (breathable and natural), linen (textured), silk (delicate and elegant), velvet (heavier and light-reducing), polyester (durable and easy-care), plus jacquard, satin, organza and sheer voile. Blackout blocks most light; dimout reduces it without always making a room fully dark. Easy-wash fabric can suit kitchens, while lined or blackout options may suit bedrooms. Check the fiber content and care label before buying.',
      chatPanel: 'Panel or Japanese curtains use wide, flat fabric panels that slide along a track. They work well for large windows, glass doors or dividing a room; panel width and count depend on the track. Make sure there is enough room on the side where the panels will stack.',
      chatMotorized: 'Motorized curtains can be controlled remotely or integrated with a smart-home system, which is useful for tall, wide or hard-to-reach windows. Match the motor and track to the curtain weight, and plan the power supply and controls in advance. Confirm compatibility with an installer.',
      chatBlackout: 'Blackout is a dense or specially coated fabric that blocks most light, useful for bedrooms, nurseries and daytime sleep. To reduce light leaking around the sides, mount the curtain wider and higher than the window, or choose a blackout roller shade. Dimout reduces light but usually does not make a room completely dark.',
      chatInstall: 'First choose a wall/rail mount or an inside-frame mount. Extending a curtain rail beyond both sides of the window helps keep open curtains from covering the glass; brackets and anchors must suit the wall and curtain weight. For roller shades and blinds, follow the product mounting guide and measurement rules.',
      chatMeasure: 'Measure the rail/window width and the drop from the rail to the floor. Pleated drapes often use about 1.5–2 times the rail width in fabric; sheers may use more fullness. Roller, Roman and inside-mounted blinds use different measurements—measure the inside width and height at several points and account for handles. Confirm the mount and final dimensions with an installer before ordering.',
      chatPrice: 'The final quote depends on fabric and yardage, window size, sewing style, hardware and installation. Catalog prices may not match custom-size orders. Share your window width/height, room and preferred style, or call +998 97 424 42 42 for a quote.',
      chatBlinds: 'Main blind types include horizontal (aluminum or wood slats), vertical fabric slats, roller shades, zebra/day-night shades and Roman shades. Horizontal slats tilt to control light; vertical blinds suit wide windows and doors. Roller shades wrap fabric around a tube, zebra shades align sheer and opaque bands, and Roman shades fold into pleats. Consider easy-clean materials for kitchens and blackout fabric for bedrooms.',
      chatRoller: 'A roller shade wraps fabric around a top tube for a neat, compact look. Light-filtering fabric softens daylight, dimout reduces it, and blackout gives stronger room darkening. It can mount inside the frame or above it; for an inside mount, check handle clearance and frame depth.',
      chatZebra: 'Zebra or day-night shades use two layers of alternating sheer and opaque bands. Sliding the layers lets you admit, soften or block more light. They look compact and modern, but choose a dedicated blackout fabric if you need strong room darkening.',
      chatRoman: 'Roman shades lift into horizontal folds and hang flat when lowered. They can be made in plain, lined or blackout fabrics and work well where space is limited. Decide whether to mount inside or outside the frame before measuring.',
      chatHorizontal: 'Horizontal blinds use aluminum, wood or moisture-resistant faux-wood slats. Tilting the slats gives precise control of light and privacy; aluminum is light and practical, while wood gives a warmer look. Consider humidity and care before choosing real wood for a kitchen.',
      chatVertical: 'Vertical blinds have long slats that slide sideways and rotate. They are useful for wide windows, patio doors and offices. Choose the slat width and stacking side, and check that the slats will clear handles and furniture.',
      chatClassic: 'Classic curtains often combine sheer curtains with heavier side panels. Finishes include tape-pleated, eyelet, hidden-hook and modern wave styles. Choose fullness based on rail width and make sure the rail can support the fabric weight.',
      chatCleaning: 'Follow the fabric care label: remove hooks and hardware, separate colors and use a gentle cycle and low temperature only when allowed. Velvet, silk, coated blackout fabrics and some blinds may need professional cleaning. Dust regularly with a soft brush or low-suction vacuum.',
      chatChoose: 'Consider four things: the room, desired light/privacy, window and mounting type, and care/budget. Blackout or lined curtains can suit bedrooms; sheers with side panels can suit living rooms; washable roller shades or shorter styles may be practical in kitchens. Tell me the room, window type and light preference and I can compare options.',
      chatOffTopic: 'Sorry, I do not have enough knowledge about that topic. I can only help with curtains, sheers, blinds, fabrics, measuring, installation, care and pricing. Please ask about one of those.',
      chatOrder: 'For an order or personal advice, call +998 97 424 42 42. Tell us the fabric you like and your window measurements, and we will help find a good option.',
      chatFallback: 'I did not understand the question. Please ask specifically about curtain styles, fabric, light control, blinds, measuring, installation, care or pricing.',
      chatError: 'Sorry, I could not get a reply just now. Please try again or call +998 97 424 42 42.',
      chatWorking: 'Preparing a reply...'
    },
    ru: {
      chatOpen: 'Консультация',
      chatTitle: 'Помощник по шторам',
      chatOnline: 'Поможем с выбором',
      chatClose: 'Закрыть чат',
      chatWelcome: 'Здравствуйте! Подскажу по классическим шторам, тюлю, blackout, рулонным и зебра-шторам, римским шторам, горизонтальным и вертикальным жалюзи. Что вас интересует?',
      chatQuestionMaterials: 'Виды штор',
      chatQuestionMeasure: 'Виды жалюзи',
      chatQuestionPrice: 'Цена и замер',
      chatGreeting: 'Здравствуйте! Спрашивайте о шторах, тюле, жалюзи, тканях, замерах, уходе или цене. Для какой комнаты выбираете?',
      chatTypes: 'Основные варианты: классические портьеры с тюлем, blackout/dimout, люверсы, шторная лента и стиль wave. Компактные решения — рулонные, зебра «день-ночь» и римские шторы; жалюзи бывают горизонтальные, вертикальные и деревянные. Для широких окон подходят панельные/японские шторы, для декора — ламбрекены и боковые полотна. Выбор зависит от комнаты, окна, света и ухода.',
      chatPlaceholder: 'Напишите ваш вопрос...',
      chatInputLabel: 'Ваше сообщение',
      chatSend: 'Отправить сообщение',
      chatMaterials: 'Для штор используют хлопок (натуральный и дышащий), лен (с выраженной фактурой), шелк (деликатный и нарядный), бархат (плотный, уменьшает свет), полиэстер (износостойкий и простой в уходе), жаккард, атлас, органзу и тюль. Blackout сильно блокирует свет, dimout уменьшает его, но не всегда дает полное затемнение. Для кухни удобна ткань, которую легко стирать, для спальни — подкладка или blackout. Перед покупкой проверьте состав и ярлык ухода.',
      chatPanel: 'Панельные, или японские, шторы состоят из широких ровных полотен, которые сдвигаются по направляющей. Подходят для больших окон, витражей и зонирования комнаты; ширина и число панелей зависят от карниза. Проверьте, достаточно ли места сбоку для собранных панелей.',
      chatMotorized: 'Электрокарниз позволяет управлять шторами дистанционно или подключить их к системе умного дома; это удобно для высоких, широких и труднодоступных окон. Мотор и направляющую подбирают под вес полотна, заранее планируют питание и управление. Совместимость и монтаж лучше подтвердить со специалистом.',
      chatBlackout: 'Blackout — плотная ткань или материал со специальным покрытием, который сильно блокирует свет; подходит для спальни, детской и дневного сна. Чтобы уменьшить засветку по краям, штору делают шире и выше окна или выбирают рулонный blackout. Dimout снижает освещенность, но обычно не обеспечивает полной темноты.',
      chatInstall: 'Сначала выберите монтаж на стену/карниз или внутрь оконной рамы. Карниз, выступающий за края окна, помогает открытым шторам не закрывать стекло; кронштейны и крепеж должны подходить стене и весу полотна. Для рулонных штор и жалюзи соблюдайте схему и правила замера производителя.',
      chatMeasure: 'Измерьте ширину карниза/окна и высоту от карниза до пола. Для складчатых портьер ткани обычно берут примерно в 1,5–2 раза больше ширины карниза; тюлю может понадобиться больше сборки. Для рулонных, римских штор и жалюзи замеры другие: при установке внутрь рамы измерьте ширину и высоту в нескольких местах, учтите ручки. Перед заказом подтвердите способ монтажа и размер со специалистом.',
      chatPrice: 'Итоговая стоимость зависит от ткани и расхода, размеров окна, пошива, карниза/фурнитуры и установки. Цена в каталоге может отличаться от индивидуального заказа. Напишите ширину и высоту окна, комнату и желаемый стиль или позвоните +998 97 424 42 42.',
      chatBlinds: 'Основные виды: горизонтальные (алюминий или дерево), вертикальные тканевые ламели, рулонные, зебра «день-ночь» и римские шторы. Горизонтальные ламели поворачиваются для регулировки света; вертикальные подходят широким окнам и дверям. Рулонные наматываются на вал, зебра совмещает прозрачные и плотные полосы, римские собираются складками. Для кухни выбирайте простой уход, для спальни — blackout.',
      chatRoller: 'Рулонная штора наматывает полотно на верхний вал и занимает мало места. Light-filtering смягчает свет, dimout заметно затемняет, blackout сильнее блокирует его. Возможен монтаж внутри рамы или сверху; при внутреннем монтаже проверьте глубину рамы и ручки.',
      chatZebra: 'Зебра («день-ночь») состоит из двух слоев с чередующимися прозрачными и плотными полосами. Сдвигая слои, можно пропускать, смягчать или сильнее перекрывать свет. Если нужно почти полное затемнение, выберите отдельную ткань blackout.',
      chatRoman: 'Римская штора при подъеме складывается горизонтальными складками, а в опущенном виде выглядит ровно. Подходит для однотонной, подкладочной или blackout ткани и экономит место. До замера решите, будет ли монтаж внутри или снаружи рамы.',
      chatHorizontal: 'Горизонтальные жалюзи бывают алюминиевыми, деревянными или из влагостойкого искусственного дерева. Поворот ламелей точно регулирует свет и приватность; алюминий легкий и практичный, дерево создает более теплый интерьер. Для кухни учитывайте влажность и уход.',
      chatVertical: 'Вертикальные жалюзи состоят из длинных ламелей, которые сдвигаются в сторону и поворачиваются. Они удобны для широких окон, балконных дверей и офисов. Заранее выберите ширину ламелей и сторону сборки, проверьте, чтобы они не задевали ручки.',
      chatClassic: 'Классические шторы часто сочетают тюль и плотные боковые портьеры. Варианты пошива: шторная лента со складками, люверсы, скрытые крючки и современный wave. Коэффициент сборки выбирают по ширине карниза, а карниз должен выдерживать вес ткани.',
      chatCleaning: 'Следуйте ярлыку ухода: снимите крючки и фурнитуру, разделите цвета; деликатная стирка и низкая температура допустимы только если это разрешено. Бархат, шелк, ткани blackout с покрытием и некоторые жалюзи могут требовать профессиональной чистки. Пыль регулярно удаляйте мягкой щеткой или пылесосом на малой мощности.',
      chatChoose: 'Учитывайте четыре вещи: комнату, нужное освещение/приватность, тип окна и монтажа, уход и бюджет. Для спальни часто выбирают blackout или подкладку, для гостиной — тюль с боковыми портьерами, для кухни — простые в уходе рулонные модели. Напишите комнату, тип окна и желаемый свет — сравню подходящие варианты.',
      chatOffTopic: 'Извините, мне не хватает знаний по этой теме. Я могу отвечать только о шторах, тюле, жалюзи, тканях, замерах, установке, уходе и ценах. Пожалуйста, задайте вопрос по одной из этих тем.',
      chatOrder: 'Для заказа или консультации позвоните: +998 97 424 42 42. Расскажите о ткани и размерах окна — поможем подобрать вариант.',
      chatFallback: 'Не поняла вопрос. Уточните, пожалуйста: вид штор, ткань, затемнение, жалюзи, замер, установка, уход или цена.',
      chatError: 'Не удалось получить ответ. Попробуйте позже или позвоните по номеру +998 97 424 42 42.',
      chatWorking: 'Готовим ответ...'
    }
  };

  function getLanguage() {
    const selected = languageSelect && languageSelect.value;
    const saved = localStorage.getItem('parda-language');
    return copyByLanguage[selected] ? selected : (copyByLanguage[saved] ? saved : 'en');
  }

  function copy() {
    return copyByLanguage[getLanguage()];
  }

  function updateLanguage() {
    const words = copy();
    root.querySelectorAll('[data-i18n]').forEach(function (element) {
      const key = element.dataset.i18n;
      if (words[key]) element.textContent = words[key];
    });
    root.querySelectorAll('[data-i18n-placeholder]').forEach(function (element) {
      const key = element.dataset.i18nPlaceholder;
      if (words[key]) element.placeholder = words[key];
    });
    root.querySelectorAll('[data-i18n-aria-label]').forEach(function (element) {
      const key = element.dataset.i18nAriaLabel;
      if (words[key]) element.setAttribute('aria-label', words[key]);
    });
  }

  function addMessage(text, kind) {
    const message = document.createElement('div');
    message.className = 'curtain-assistant-message is-' + kind;
    message.textContent = text;
    messages.appendChild(message);
    messages.scrollTop = messages.scrollHeight;
    return message;
  }

  function localReply(question) {
    const text = question.toLocaleLowerCase().replace(/[’‘`]/g, "'");
    const matches = function (terms) {
      return terms.some(function (term) { return text.includes(term); });
    };
    const words = {
      greeting: ['salom', 'assalomu alaykum', 'hello', 'hi', 'привет', 'здравствуйте', 'добрый день'],
      curtainTopic: ['parda', 'pardalar', 'shtor', 'штор', 'занавес', 'tyul', 'тюл', 'jalyuz', 'жалюз', 'blind', 'curtain', 'drape', 'sheer', 'roller', 'roman shade', 'fabric', 'mato', 'материал', 'ткан', 'blackout', 'dimout', 'lyuvers', 'люверс', 'karniz', 'карниз', 'deraza', 'окно', 'window', 'панел', 'panel', 'yapon', 'япон', 'электрокарниз', 'motorized', 'motor', 'motorli', 'montaj', 'o\'rnat', 'установ', 'монтаж', 'карниз'],
      type: ['turlari', 'turi', 'qanday turl', 'qanaqa turl', 'types', 'style', 'стиль', 'виды', 'какие бывают'],
      measure: ["o'lch", 'olch', 'размер', 'замер', 'измер', 'measure', 'width', 'height', 'kenglik', 'balandlik', 'eni', 'bo\'yi'],
      price: ['narx', 'qancha', 'price', 'cost', 'сколько', 'цен', 'стоим', 'hisob'],
      cleaning: ['parvarish', 'tozalash', 'yuvish', 'clean', 'wash', 'care', 'уход', 'стир', 'чист'],
      choose: ['qaysi', 'tanlash', 'mos kel', 'tavsiya', 'yaxshi', 'choose', 'recommend', 'best', 'подобрать', 'выбрать', 'лучше', 'совет'],
      roller: ['rolik', 'рулон', 'roller'],
      zebra: ['zebra', 'зебра', 'kun-tun', 'день-ночь'],
      roman: ['rim', 'рим', 'roman shade'],
      horizontal: ['gorizontal', 'горизонтал', 'horizontal'],
      vertical: ['vertikal', 'вертикал', 'vertical'],
      classic: ['klassik', 'classic', 'классичес', 'lyuvers', 'люверс', 'wave', 'burma', 'складк', 'tyul', 'тюл'],
      materials: ['mato', 'мат', 'fabric', 'silk', 'linen', 'cotton', 'velvet', 'бархат', 'ткан', 'material', 'baxmal', 'zig', 'ipak', 'paxta', 'organza', 'atlas', 'jacquard'],
      panel: ['panel', 'панел', 'yapon', 'япон'],
      motorized: ['motorli', 'электрокарниз', 'электрическ', 'motorized', 'motor curtain', 'smart curtain'],
      blackout: ['blackout', 'блэкаут', 'блэкаут', 'dimout', 'дим-аут'],
      install: ['montaj', 'o\'rnat', 'o’rnat', 'установ', 'монтаж', 'install', 'mount'],
      blinds: ['jalyuz', 'жалюз', 'blind', 'jalousie', 'жалюзи'],
      order: ['buyurt', 'zakaz', 'order', 'bog\'lan', 'связ', 'контакт', 'telefon', 'phone', 'номер']
    };
    const allTypeWords = ['parda', 'pardalar', 'штор', 'curtain', 'shtor'];

    if (matches(words.greeting)) return copy().chatGreeting;
    if (matches(words.motorized)) return copy().chatMotorized;
    if (matches(words.panel)) return copy().chatPanel;
    if (matches(words.blackout)) return copy().chatBlackout;
    if (matches(words.roller)) return copy().chatRoller;
    if (matches(words.zebra)) return copy().chatZebra;
    if (matches(words.roman)) return copy().chatRoman;
    if (matches(words.horizontal)) return copy().chatHorizontal;
    if (matches(words.vertical)) return copy().chatVertical;
    if (matches(words.cleaning)) return copy().chatCleaning;
    if (matches(words.install)) return copy().chatInstall;
    if (matches(words.measure)) return copy().chatMeasure;
    if (matches(words.price)) return copy().chatPrice;
    if (matches(words.materials)) return copy().chatMaterials;
    if (matches(words.order)) return copy().chatOrder;
    if (matches(words.classic)) return copy().chatClassic;
    if (matches(words.choose)) return copy().chatChoose;
    if (matches(words.blinds)) return copy().chatBlinds;
    if (matches(words.type) || (matches(allTypeWords) && text.split(/\s+/).length <= 4)) return copy().chatTypes;
    if (matches(words.curtainTopic)) return copy().chatFallback;
    return copy().chatOffTopic;
  }

  async function requestAssistantReply(question) {
    const endpoint = root.dataset.apiEndpoint.trim();
    if (!endpoint) return localReply(question);

    const url = new URL(endpoint, window.location.href);
    if (url.origin !== window.location.origin) {
      throw new Error('Assistant API endpoint must be same-origin.');
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
    const headers = { 'Content-Type': 'application/json' };
    if (csrfToken) headers['X-CSRFToken'] = csrfToken;

    const response = await fetch(url.href, {
      method: 'POST',
      credentials: 'same-origin',
      headers: headers,
      body: JSON.stringify({
        message: question,
        language: getLanguage(),
        history: conversation.slice(-9, -1)
      })
    });
    if (!response.ok) throw new Error('Assistant API returned HTTP ' + response.status + '.');

    const result = await response.json();
    if (!result || typeof result.reply !== 'string' || !result.reply.trim()) {
      throw new Error('Assistant API response must contain a non-empty "reply" string.');
    }
    return result.reply.trim();
  }

  function setOpen(open) {
    window.clearTimeout(closeTimer);
    toggle.setAttribute('aria-expanded', String(open));
    panel.setAttribute('aria-hidden', String(!open));
    if (open) {
      panel.hidden = false;
      window.requestAnimationFrame(function () { panel.classList.add('is-open'); });
      input.focus();
    } else {
      panel.classList.remove('is-open');
      closeTimer = window.setTimeout(function () {
        if (toggle.getAttribute('aria-expanded') === 'false') panel.hidden = true;
      }, 190);
      toggle.focus();
    }
  }

  async function sendMessage(text) {
    const question = text.trim();
    if (!question || sendButton.disabled) return;
    suggestions.hidden = true;
    addMessage(question, 'user');
    conversation.push({ role: 'user', content: question });
    input.value = '';
    sendButton.disabled = true;
    status.textContent = copy().chatWorking;
    const typing = addMessage(copy().chatWorking, 'typing');

    try {
      const answer = await requestAssistantReply(question);
      typing.remove();
      addMessage(answer, 'assistant');
      conversation.push({ role: 'assistant', content: answer });
      if (conversation.length > 20) conversation.splice(0, conversation.length - 20);
      status.textContent = '';
    } catch (error) {
      console.error('Curtain advisor request failed:', error);
      typing.remove();
      addMessage(copy().chatError, 'assistant');
      status.textContent = copy().chatError;
    } finally {
      sendButton.disabled = false;
      input.focus();
    }
  }

  toggle.addEventListener('click', function () {
    setOpen(toggle.getAttribute('aria-expanded') !== 'true');
  });
  closeButton.addEventListener('click', function () { setOpen(false); });
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    sendMessage(input.value);
  });
  suggestions.addEventListener('click', function (event) {
    const button = event.target.closest('[data-assistant-question]');
    if (button && copy()[button.dataset.assistantQuestion]) {
      sendMessage(copy()[button.dataset.assistantQuestion]);
    }
  });
  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && toggle.getAttribute('aria-expanded') === 'true') setOpen(false);
  });
  if (languageSelect) languageSelect.addEventListener('change', updateLanguage);
  updateLanguage();
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      window.setTimeout(updateLanguage, 0);
    }, { once: true });
  }
})();
