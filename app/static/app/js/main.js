// ANDROID ANIQLASH — faqat Android qurilmalarga yengil uslublar (blur o'chirish va h.k.)
// berish uchun. iPhone va boshqa qurilmalar uslubi o'zgarmaydi.
// Sahifa bo'yalmay qolmasligi uchun DOMContentLoaded'ni kutmasdan darhol qo'shiladi.
(function () {
  try {
    if (/Android/i.test(navigator.userAgent || '')) {
      document.documentElement.classList.add('is-android');
    }
  } catch (error) {
    /* UA o'qib bo'lmasa — hech narsa qo'shilmaydi, standart uslub qo'llanadi */
  }
})();

// TASHRIF HISOBLAGICHI — har sahifa ochilganda 0 dan haqiqiy songacha animatsiya
(function () {
  function formatCount(value) {
    try {
      return value.toLocaleString('ru-RU');
    } catch (error) {
      return String(value);
    }
  }

  function animateVisitCounter(element) {
    const target = Number.parseInt(element.dataset.visitCounter, 10);
    if (!Number.isFinite(target) || target < 0) return;

    const prefersReducedMotion = window.matchMedia
      && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    if (prefersReducedMotion || target === 0) {
      element.textContent = formatCount(target);
      return;
    }

    const duration = 1200;
    const startTime = performance.now();

    function step(now) {
      const progress = Math.min((now - startTime) / duration, 1);
      const eased = 1 - Math.pow(1 - progress, 3);
      element.textContent = formatCount(Math.round(target * eased));
      if (progress < 1) window.requestAnimationFrame(step);
    }

    element.textContent = '0';
    window.requestAnimationFrame(step);
  }

  function initVisitCounters() {
    document.querySelectorAll('[data-visit-counter]').forEach(function (element) {
      if (element.dataset.visitCounted === '1') return;
      element.dataset.visitCounted = '1';
      animateVisitCounter(element);
    });
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initVisitCounters);
  } else {
    initVisitCounters();
  }
  document.addEventListener('turbo:load', initVisitCounters);
})();

let pageAbortController = null;

function initSitePage() {
  // Turbo bilan sahifa almashganda eski document/window tinglovchilarini tozalaymiz
  if (pageAbortController) pageAbortController.abort();
  pageAbortController = new AbortController();
  const pageSignal = pageAbortController.signal;

  const gallery = document.querySelector('.gallery-grid');
  const languageSelect = document.getElementById('language-select');
  const profileToggle = document.querySelector('[data-profile-toggle]');
  const profileMenu = document.querySelector('[data-profile-menu]');
  const translations = {
    en: { catalogLink: 'Catalog', catalogTitle: 'CURTAIN CATALOG', download: 'Download catalog', showing: 'Showing', products: 'products', sort: 'Name', emptyProducts: 'No products available yet.', searchPlaceholder: 'Search curtains by name, color, material…', searchBtn: 'Search', resultsFor: 'Results for', favoritesTitle: 'My favorites', emptyFavorites: 'You have no favorite curtains yet.', loginForFavorites: 'Please sign in to save favorites.', back: '← Back', signIn: 'Sign in', register: 'Create account', logout: 'Log out', addProduct: 'Add product', deleteProduct: 'Delete product', origin: 'Origin:', curtainName: 'Curtain name', fabric: 'Fabric / material', standardLength: 'Standard length (m)', price: 'Price ($)', colorField: 'Color', originCountry: 'Origin country', roomCategory: 'Room / category', imageFile: 'Curtain image file', imageHint: 'JPG, PNG, WEBP or HEIC image', description: 'Description', highlightProduct: 'Show in catalog highlights', activeProduct: 'Active product', cancel: 'Cancel', saveProduct: 'Add to catalog', welcomeBack: 'Welcome back', signInTitle: 'Sign in', signInSubtitle: 'Continue to your SHTOR HOUSE account.', emailUsername: 'Email or username', password: 'Password', continue: 'Continue', forgot: 'Forgot password?', or: 'or', google: 'Continue with Google', noAccount: 'Don\'t have an account?', signUp: 'Sign up', googleNotConfigured: 'Google sign-in is not configured yet.', googleSessionExpired: 'Google sign-in session expired. Please try again.', googleCancelled: 'Google sign-in was cancelled.', googleFailed: 'Google sign-in could not be completed.', googleEmailFailed: 'Google did not provide a verified email address.', category_all: 'All', category_living_room: 'Living room', category_bedroom: 'Bedroom', category_kitchen: 'Kitchen', category_office: 'Office', category_custom: 'Custom' },
    uz: { catalogLink: 'Katalog', catalogTitle: 'PARDA KATALOGI', download: 'Katalogni yuklash', showing: 'Jami', products: 'mahsulot', sort: 'Nomi', emptyProducts: 'Hozircha mahsulot mavjud emas.', searchPlaceholder: 'Pardani nomi, rangi, matosi bo‘yicha qidiring…', searchBtn: 'Qidirish', resultsFor: 'Natijalar:', favoritesTitle: 'Sevimlilarim', emptyFavorites: 'Hozircha sevimli pardangiz yo‘q.', loginForFavorites: 'Sevimlilarni saqlash uchun tizimga kiring.', back: '← Orqaga', signIn: 'Kirish', register: 'Akkaunt yaratish', logout: 'Chiqish', addProduct: 'Mahsulot qo‘shish', deleteProduct: 'Mahsulotni o‘chirish', origin: 'Kelib chiqishi:', curtainName: 'Parda nomi', fabric: 'Mato turi', standardLength: 'Standart uzunlik (m)', price: 'Narxi ($)', colorField: 'Rang', originCountry: 'Kelib chiqqan mamlakat', roomCategory: 'Xona / kategoriya', imageFile: 'Parda rasmi', imageHint: 'JPG, PNG, WEBP yoki HEIC rasm', description: 'Tavsif', highlightProduct: 'Katalogda ajratib ko‘rsatish', activeProduct: 'Faol mahsulot', cancel: 'Bekor qilish', saveProduct: 'Katalogga qo‘shish', welcomeBack: 'Xush kelibsiz', signInTitle: 'Kirish', signInSubtitle: 'SHTOR HOUSE akkauntingizga kiring.', emailUsername: 'Email yoki foydalanuvchi nomi', password: 'Parol', continue: 'Davom etish', forgot: 'Parolni unutdingizmi?', or: 'yoki', google: 'Google orqali kirish', noAccount: 'Akkauntingiz yo‘qmi?', signUp: 'Ro‘yxatdan o‘tish', googleNotConfigured: 'Google orqali kirish hali sozlanmagan.', googleSessionExpired: 'Google sessiyasi tugadi. Qayta urinib ko‘ring.', googleCancelled: 'Google orqali kirish bekor qilindi.', googleFailed: 'Google orqali kirish yakunlanmadi.', googleEmailFailed: 'Google tasdiqlangan email bermadi.', category_all: 'Barchasi', category_living_room: 'Mehmonxona', category_bedroom: 'Yotoqxona', category_kitchen: 'Oshxona', category_office: 'Ofis', category_custom: 'Maxsus' },
    ru: { catalogLink: 'Каталог', catalogTitle: 'КАТАЛОГ ШТОР', download: 'Скачать каталог', showing: 'Показано', products: 'товаров', sort: 'Название', emptyProducts: 'Товаров пока нет.', searchPlaceholder: 'Поиск штор по названию, цвету, ткани…', searchBtn: 'Поиск', resultsFor: 'Результаты:', favoritesTitle: 'Мои избранные', emptyFavorites: 'У вас пока нет избранных штор.', loginForFavorites: 'Войдите, чтобы сохранять избранное.', back: '← Назад', signIn: 'Войти', register: 'Создать аккаунт', logout: 'Выйти', addProduct: 'Добавить товар', deleteProduct: 'Удалить товар', origin: 'Происхождение:', curtainName: 'Название шторы', fabric: 'Ткань / материал', standardLength: 'Стандартная длина (м)', price: 'Цена ($)', colorField: 'Цвет', originCountry: 'Страна происхождения', roomCategory: 'Комната / категория', imageFile: 'Файл изображения', imageHint: 'Изображение JPG, PNG, WEBP или HEIC', description: 'Описание', highlightProduct: 'Показывать в подборке', activeProduct: 'Активный товар', cancel: 'Отмена', saveProduct: 'Добавить в каталог', welcomeBack: 'С возвращением', signInTitle: 'Войти', signInSubtitle: 'Войдите в аккаунт SHTOR HOUSE.', emailUsername: 'Email или имя пользователя', password: 'Пароль', continue: 'Продолжить', forgot: 'Забыли пароль?', or: 'или', google: 'Войти через Google', noAccount: 'Нет аккаунта?', signUp: 'Регистрация', googleNotConfigured: 'Вход через Google пока не настроен.', googleSessionExpired: 'Сессия Google истекла. Попробуйте снова.', googleCancelled: 'Вход через Google отменен.', googleFailed: 'Не удалось завершить вход через Google.', googleEmailFailed: 'Google не предоставил подтвержденный email.', category_all: 'Все', category_living_room: 'Гостиная', category_bedroom: 'Спальня', category_kitchen: 'Кухня', category_office: 'Офис', category_custom: 'На заказ' }
  };
  const extraTranslations = {
    en: {
      registerEyebrow: 'Welcome', registerTitle: 'Create account', alreadyAccount: 'Already have an account?', logIn: 'Log in',
      registeredUsers: 'registered customers', featuredCurtains: 'Featured curtains',
      curtainShowcaseEyebrow: 'A little inspiration for your home',
      curtainShowcaseTitle: 'Find your perfect window style',
      curtainShowcaseHint: 'Curtains, blinds and more — explore the collection.',
      pauseShowcase: 'Pause animation', resumeShowcase: 'Resume animation',
      heroEyebrow: 'Thoughtful details. A warmer home.',
      heroTitle: 'The right curtains can change the whole feeling of a room.',
      heroDescription: 'Explore curtains and blinds by room, color and material, then find the style that feels like home.',
      heroExplore: 'Explore the collection', heroContact: 'Talk to our team',
      heroNote: 'A little detail can make a space feel entirely yours.',
      heroImageEyebrow: 'Your home, your style', heroScroll: 'Discover your style',
      benefitsEyebrow: 'Made for the way you live',
      benefitsTitle: 'Finding your style should feel easy.',
      benefitRoomTitle: 'A style for every room',
      benefitRoomText: 'Browse ideas for living rooms, bedrooms, kitchens and more.',
      benefitSearchTitle: 'Explore at your pace',
      benefitSearchText: 'Filter by category or search by color, fabric and style.',
      benefitFavoriteTitle: 'Keep your favorites close',
      benefitFavoriteText: 'Save the curtains you love and come back to them anytime.',
      featuredCollection: 'SHTOR HOUSE selection', featuredCurtainsTitle: 'Curtains made to inspire',
      previousCurtains: 'Previous curtains', nextCurtains: 'Next curtains',
      pageSignIn: 'Sign in | SHTOR HOUSE', pageRegister: 'Register | SHTOR HOUSE', pageAddProduct: 'Add Product | SHTOR HOUSE',
      pageFavorites: 'My favorites | SHTOR HOUSE', pageReset: 'Reset password | SHTOR HOUSE', pageResetDone: 'Email sent | SHTOR HOUSE',
      pageResetConfirm: 'New password | SHTOR HOUSE', pageResetComplete: 'Password updated | SHTOR HOUSE',
      catalog: 'Catalog', share: 'Share', inStock: 'In stock', material: 'Material:', length: 'Length:', color: 'Color:',
      style: 'Style:', premiumLayered: 'Premium layered', favorite: '☆ Add to favorites', buy: 'Buy now',
      purchase: 'Purchase request', contactAbout: 'Contact us about', contactText: 'Choose the easiest way to reach us and we will help you complete your order.',
      deleteConfirm: 'Delete this product permanently?', footerTagline: 'Curtains made for beautiful spaces', locationLabel: 'Location', phoneLabel: 'Phone',
      addImage: 'Download image', viewProduct: 'View product', removeFavorite: 'Remove from favorites',
      welcomeRegister: 'Welcome', username: 'Username', email: 'Email', newPassword: 'New password',
      confirmPassword: 'Confirm new password', passwordHelp: 'Your password must be at least 8 characters and not too common.',
      accountRecovery: 'Account recovery', resetTitle: 'Reset password', resetSubtitle: 'Enter your account email and we will send reset instructions.',
      sendResetLink: 'Send reset link', backSignIn: 'Back to sign in', checkInbox: 'Check your inbox', emailSent: 'Email sent',
      resetSentInfo: 'If an account exists for that email, reset instructions have been sent.', allSet: 'All set',
      passwordUpdated: 'Password updated', passwordUpdatedInfo: 'Your password has been changed successfully.', signInNow: 'Sign in now',
      setNewPassword: 'Set new password', invalidResetLink: 'This reset link is no longer valid.', requestNewLink: 'Request a new link',
      selectLanguage: 'Select language', toggleTheme: 'Toggle light and dark mode', gridView: 'Grid view', listView: 'List view',
      sortProducts: 'Sort products by name', categoryFilters: 'Category filters', catalogView: 'Catalog view', collectionGallery: 'Collection gallery',
      favoritesGallery: 'Favorites gallery', productActions: 'Product actions', searchProducts: 'Search products', clearSearch: 'Clear search',
      loginRequired: 'Please sign in to save favorites.', favoriteError: 'Could not update favorites. Please try again.',
      modalHelp: 'We are ready to help you choose the perfect curtain for your space.', continue: 'Continue',
      modalSend: 'Send us your room details', modalRequest: 'Request a custom curtain consultation',
      modalDesign: 'Choose a style for your interior', modalAlbums: 'Browse our featured curtain collection',
      modalHelpTitle: 'Contact SHTOR HOUSE support', close: 'Close', tashkentUzbekistan: 'Tashkent, Uzbekistan',
      openMap: 'Open map',
      maintenanceLabel: 'Service update', serviceUnavailableTitle: 'Something went wrong',
      serviceUnavailableMessage: 'The Telegram service is not available right now. We are working to fix it.',
      accountCreated: 'Account created successfully.',
      quoteSubmitted: 'Your quote request has been submitted successfully.',
      requestSent: 'Your request has been sent successfully.',
      productDeleted: 'Product deleted successfully.',
      staffDeleteOnly: 'Only an administrator can delete products.',
      staffAddOnly: 'Only an administrator can add products.',
      productAddedSuffix: 'was added successfully.',
      priceFilter: 'Price ($)', priceFrom: 'From', priceTo: 'To', applyFilter: 'Filter', resetFilters: 'Reset',
      minPrice: 'Minimum price', maxPrice: 'Maximum price',
      sort_featured: 'Featured first', sort_newest: 'Newest first', sort_price_asc: 'Price: low to high',
      sort_price_desc: 'Price: high to low', sort_name_asc: 'Name: A–Z', sort_name_desc: 'Name: Z–A',
      dashboard: 'Dashboard', pageDashboard: 'Statistics | SHTOR HOUSE', backToCatalog: 'Catalog',
      dashboardEyebrow: 'Administrator panel', dashboardTitle: 'Site statistics',
      dashboardSubtitle: 'A live overview of visits, products and customer requests.',
      liveOverview: 'Live overview', keyMetrics: 'Key metrics',
      statVisits: 'Site visits', statAllTime: 'all time', statProducts: 'Products', statActiveNow: 'active',
      statRequests: 'Quote requests', statLastSevenDays: 'in the last 7 days', statUsers: 'Users', statNewUsers: 'joined this week',
      statFavorites: 'Favorites', statSavedCurtains: 'saved curtains', statNewRequests: 'New requests', statLastSevenDaysOnly: 'last 7 days',
      chartTitle: 'Requests in the last 7 days', chartSubtitle: 'Daily activity', chartAria: 'Requests per day',
      chartEmpty: 'No requests in the last 7 days.', categoryTitle: 'Products by category', noProductsYet: 'No products yet.',
      topViewedTitle: 'Most viewed curtains', topViewedSubtitle: 'by page views', noViewsYet: 'No views yet.', viewsLabel: 'views',
      topRequestedTitle: 'Most requested curtains', topRequestedSubtitle: 'by quote requests', noRequestsYet: 'No requests yet.', requestsLabel: 'requests',
      recentRequestsTitle: 'Recent quote requests', recentRequestsSubtitle: 'latest 12',
      tableCustomer: 'Customer', tablePhone: 'Phone', tableProduct: 'Product', tableDate: 'Date', tablePrice: 'Price', tableStatus: 'Status', tableViews: 'Views',
      recentProductsTitle: 'Recently added products', openCatalog: 'Open catalog',
      statusActive: 'Active', statusInactive: 'Inactive', statusFeatured: 'Featured',
      dashboardFootnote: 'Only administrators can see this page.',
      adminOnly: 'Only an administrator can open the dashboard.',
      // Admin bell & notifications
      notifications: 'Notifications', unread: 'unread', allRead: 'All read', markAllRead: 'Mark all read',
      noNotifications: 'No notifications yet.', viewAllNotifications: 'View all notifications',
      notifToastTitle: 'New notifications', notifToastText: 'new activity from your customers', notifToastOpen: 'Open',
      notifLoginGoogle: 'signed in with Google', notifLoginPassword: 'signed in with password',
      notifRegistered: 'created an account', notifRegisteredLong: 'Created a new account on the site.',
      notifFavorited: 'added to favorites', notifFavoritedLong: 'Added a curtain to favorites:',
      notifMessage: 'sent a message to the administrator', notifMessageLong: 'Sent a message to the administrator.',
      notifKindLogin: 'Sign-ins', notifKindRegister: 'Registrations', notifKindFavorite: 'Favorites', notifKindMessage: 'Messages',
      filterUnread: 'Unread', viaGoogle: 'via Google', viaPassword: 'via password',
      // Users page
      users: 'Users', pageUsers: 'Users | SHTOR HOUSE', usersEyebrow: 'Audience', usersTitle: 'Users',
      usersSubtitle: 'See how every customer signed in, what they saved to favorites and block accounts when needed.',
      usersLive: 'Live audience', usersFootnote: 'Only administrators can see user activity and block accounts.',
      userJoined: 'Joined', userLastLogin: 'Last sign-in', userSignIns: 'Sign-ins',
      userFavorites: 'Favorites', userNoFavorites: 'No favorite curtains yet.',
      userNeverSignedIn: 'Not signed in yet', filterAll: 'All', filterGoogle: 'Google', filterPassword: 'Password', filterBlocked: 'Blocked',
      blockedLabel: 'blocked', blockUser: 'Block', blockUserConfirm: 'Block this user? They will not be able to sign in.',
      unblockUser: 'Unblock', unblockUserConfirm: 'Unblock this user?',
      statAllUsers: 'All users', statRegisteredAccounts: 'registered accounts',
      statGoogleUsers: 'Google accounts', statGoogleLogins: 'Google sign-ins',
      statPasswordUsers: 'Password accounts', statPasswordLogins: 'password sign-ins',
      statBlockedUsers: 'Blocked', statBlockedHint: 'cannot sign in',
      viewAllUsers: 'All users',
      // Contact admin
      contactBackToProduct: 'Back to product', adminContactEyebrow: 'Direct message', adminContactTitle: 'Write to the administrator',
      adminContactSubtitle: 'Ask a question, request a custom size or share a special wish — the message goes straight to the shop administrator.',
      adminContactFormTitle: 'Your message', adminContactPrivate: 'Only the administrator sees this',
      msgFullName: 'Your name', msgNamePlaceholder: 'Your full name', msgEmail: 'Email', msgEmailPlaceholder: 'you@example.com',
      msgPhone: 'Phone', msgPhonePlaceholder: '+998 90 123 45 67', msgText: 'Message', msgTextPlaceholder: 'Write your message to the administrator…',
      phoneInvalid: 'Enter exactly 9 digits after +998.',
      msgSend: 'Send message', adminContactNote: 'We usually reply within one working day.',
      pageContactAdmin: 'Message to administrator | SHTOR HOUSE',
      writeToAdmin: 'Write to administrator',
      // Notifications page
      notificationsEyebrow: 'Activity feed', notificationsTitle: 'Notifications', notificationsSubtitle: 'Every sign-in, favorite and message from your customers, collected in one place.',
      notificationsFootnote: 'Only administrators can see this activity.', notificationFilters: 'Notification filters',
      viewUser: 'View user',
      // Product detail
      contactAbout: 'Contact us about', contactText: 'Choose the easiest way to reach us and we will help you complete your order.',
    },
    uz: {
      registerEyebrow: 'Xush kelibsiz', registerTitle: 'Akkaunt yaratish', alreadyAccount: 'Akkauntingiz bormi?', logIn: 'Kirish',
      registeredUsers: 'ro‘yxatdan o‘tgan mijozlar', featuredCurtains: 'Tanlangan pardalar',
      curtainShowcaseEyebrow: 'Uyingiz uchun ilhom',
      curtainShowcaseTitle: 'Derazangizga mos uslubni tanlang',
      curtainShowcaseHint: 'Pardalar, jalyuzilar va boshqa nafis yechimlar.',
      pauseShowcase: 'Animatsiyani to‘xtatish', resumeShowcase: 'Animatsiyani davom ettirish',
      heroEyebrow: 'Nozik detallar. Shinam xonadon.',
      heroTitle: 'To‘g‘ri tanlangan parda xona kayfiyatini o‘zgartiradi.',
      heroDescription: 'Parda va jalyuzilarni xona, rang va mato bo‘yicha ko‘rib, uyingizga mos uslubni toping.',
      heroExplore: 'To‘plamni ko‘rish', heroContact: 'Biz bilan bog‘lanish',
      heroNote: 'Nozik bir detal ham makonni o‘zingiznikidek his qildiradi.',
      heroImageEyebrow: 'Uyingiz — uslubingiz', heroScroll: 'Uslubingizni kashf eting',
      benefitsEyebrow: 'Hayot tarzingizga mos',
      benefitsTitle: 'O‘zingizga mos uslubni topish oson bo‘lsin.',
      benefitRoomTitle: 'Har bir xona uchun uslub',
      benefitRoomText: 'Mehmonxona, yotoqxona, oshxona va boshqa xonalar uchun g‘oyalarni ko‘ring.',
      benefitSearchTitle: 'O‘zingizga qulay tarzda tanlang',
      benefitSearchText: 'Kategoriya orqali saralang yoki rang, mato va uslub bo‘yicha qidiring.',
      benefitFavoriteTitle: 'Yoqtirganlaringizni saqlang',
      benefitFavoriteText: 'Yoqtirgan pardalaringizni sevimlilarga qo‘shib, istalgan vaqtda qayting.',
      featuredCollection: 'SHTOR HOUSE tanlovi', featuredCurtainsTitle: 'Ilhom beruvchi pardalar',
      previousCurtains: 'Oldingi pardalar', nextCurtains: 'Keyingi pardalar',
      pageSignIn: 'Kirish | SHTOR HOUSE', pageRegister: 'Ro‘yxatdan o‘tish | SHTOR HOUSE', pageAddProduct: 'Mahsulot qo‘shish | SHTOR HOUSE',
      pageFavorites: 'Sevimlilarim | SHTOR HOUSE', pageReset: 'Parolni tiklash | SHTOR HOUSE', pageResetDone: 'Xat yuborildi | SHTOR HOUSE',
      pageResetConfirm: 'Yangi parol | SHTOR HOUSE', pageResetComplete: 'Parol yangilandi | SHTOR HOUSE',
      catalog: 'Katalog', share: 'Ulashish', inStock: 'Mavjud', material: 'Mato:', length: 'Uzunligi:', color: 'Rangi:',
      style: 'Uslubi:', premiumLayered: 'Ko‘p qatlamli premium', favorite: '☆ Sevimlilarga qo‘shish', buy: 'Sotib olish',
      purchase: 'Xarid so‘rovi', contactAbout: 'Mahsulot haqida bog‘lanish', contactText: 'Biz bilan bog‘lanish usulini tanlang, buyurtmangizni rasmiylashtirishga yordam beramiz.',
      deleteConfirm: 'Bu mahsulot butunlay o‘chirilsinmi?', footerTagline: 'Chiroyli makonlar uchun pardalar', locationLabel: 'Manzil', phoneLabel: 'Telefon',
      addImage: 'Rasmni yuklab olish', viewProduct: 'Mahsulotni ko‘rish', removeFavorite: 'Sevimlilardan olib tashlash',
      welcomeRegister: 'Xush kelibsiz', username: 'Foydalanuvchi nomi', email: 'Email', newPassword: 'Yangi parol',
      confirmPassword: 'Yangi parolni tasdiqlang', passwordHelp: 'Parol kamida 8 ta belgidan iborat va juda oddiy bo‘lmasligi kerak.',
      accountRecovery: 'Akkauntni tiklash', resetTitle: 'Parolni tiklash', resetSubtitle: 'Email manzilingizni kiriting, tiklash ko‘rsatmalarini yuboramiz.',
      sendResetLink: 'Tiklash havolasini yuborish', backSignIn: 'Kirish sahifasiga qaytish', checkInbox: 'Pochtangizni tekshiring', emailSent: 'Xat yuborildi',
      resetSentInfo: 'Agar bu emailga akkaunt bog‘langan bo‘lsa, parolni tiklash ko‘rsatmalari yuborildi.', allSet: 'Tayyor',
      passwordUpdated: 'Parol yangilandi', passwordUpdatedInfo: 'Parolingiz muvaffaqiyatli o‘zgartirildi.', signInNow: 'Kirish',
      setNewPassword: 'Yangi parolni saqlash', invalidResetLink: 'Parolni tiklash havolasi yaroqsiz.', requestNewLink: 'Yangi havola so‘rash',
      selectLanguage: 'Tilni tanlang', toggleTheme: 'Yorug‘ va qorong‘i rejimni almashtirish', gridView: 'Katakcha ko‘rinishi', listView: 'Ro‘yxat ko‘rinishi',
      sortProducts: 'Mahsulotlarni nomi bo‘yicha saralash', categoryFilters: 'Kategoriya filtrlari', catalogView: 'Katalog ko‘rinishi', collectionGallery: 'To‘plam galereyasi',
      favoritesGallery: 'Sevimlilar galereyasi', productActions: 'Mahsulot amallari', searchProducts: 'Mahsulotlarni qidirish', clearSearch: 'Qidiruvni tozalash',
      loginRequired: 'Sevimlilarga qo‘shish uchun tizimga kiring.', favoriteError: 'Sevimlilarni yangilab bo‘lmadi. Qayta urinib ko‘ring.',
      modalHelp: 'Sizga mos pardani tanlashda yordam berishga tayyormiz.', continue: 'Davom etish',
      modalSend: 'Xonangiz haqida ma’lumot yuboring', modalRequest: 'Maxsus parda bo‘yicha maslahat so‘rash',
      modalDesign: 'Interyeringiz uchun uslub tanlang', modalAlbums: 'Tanlangan pardalar to‘plamini ko‘ring',
      modalHelpTitle: 'SHTOR HOUSE yordam xizmatiga murojaat', close: 'Yopish', tashkentUzbekistan: 'Toshkent, O‘zbekiston',
      openMap: 'Xaritani ochish',
      maintenanceLabel: 'Xizmat holati', serviceUnavailableTitle: 'Xatolik yuz berdi',
      serviceUnavailableMessage: 'Telegram xizmati hozircha ishlamayapti. Uni tuzatish ustida ishlayapmiz.',
      accountCreated: 'Akkaunt muvaffaqiyatli yaratildi.',
      quoteSubmitted: 'So‘rov muvaffaqiyatli yuborildi.',
      requestSent: 'So‘rovingiz muvaffaqiyatli yuborildi.',
      productDeleted: 'Mahsulot muvaffaqiyatli o‘chirildi.',
      staffDeleteOnly: 'Mahsulotni faqat administrator o‘chira oladi.',
      staffAddOnly: 'Mahsulotni faqat administrator qo‘sha oladi.',
      productAddedSuffix: 'muvaffaqiyatli qo‘shildi.',
      priceFilter: 'Narx ($)', priceFrom: 'dan', priceTo: 'gacha', applyFilter: 'Filtrlash', resetFilters: 'Tozalash',
      minPrice: 'Eng kam narx', maxPrice: 'Eng yuqori narx',
      sort_featured: 'Avval tavsiya etilganlar', sort_newest: 'Avval yangilari', sort_price_asc: 'Narx: arzon → qimmat',
      sort_price_desc: 'Narx: qimmat → arzon', sort_name_asc: 'Nomi: A–Z', sort_name_desc: 'Nomi: Z–A',
      dashboard: 'Statistika', pageDashboard: 'Statistika | SHTOR HOUSE', backToCatalog: 'Katalog',
      dashboardEyebrow: 'Administrator paneli', dashboardTitle: 'Sayt statistikasi',
      dashboardSubtitle: 'Tashriflar, mahsulotlar va mijoz so‘rovlarining jonli ko‘rinishi.',
      liveOverview: 'Jonli ko‘rinish', keyMetrics: 'Asosiy ko‘rsatkichlar',
      statVisits: 'Sayt tashriflari', statAllTime: 'jami', statProducts: 'Mahsulotlar', statActiveNow: 'faol',
      statRequests: 'Xarid so‘rovlari', statLastSevenDays: 'oxirgi 7 kunda', statUsers: 'Foydalanuvchilar', statNewUsers: 'shu haftada qo‘shilgan',
      statFavorites: 'Sevimlilar', statSavedCurtains: 'saqlangan pardalar', statNewRequests: 'Yangi so‘rovlar', statLastSevenDaysOnly: 'oxirgi 7 kun',
      chartTitle: 'Oxirgi 7 kundagi so‘rovlar', chartSubtitle: 'Kunlik faollik', chartAria: 'Kuniga so‘rovlar',
      chartEmpty: 'Oxirgi 7 kunda so‘rov yo‘q.', categoryTitle: 'Kategoriya bo‘yicha mahsulotlar', noProductsYet: 'Hozircha mahsulot yo‘q.',
      topViewedTitle: 'Eng ko‘p ko‘rilgan pardalar', topViewedSubtitle: 'sahifa ko‘rishlari bo‘yicha', noViewsYet: 'Hozircha ko‘rishlar yo‘q.', viewsLabel: 'ko‘rish',
      topRequestedTitle: 'Eng ko‘p so‘ralgan pardalar', topRequestedSubtitle: 'xarid so‘rovlari bo‘yicha', noRequestsYet: 'Hozircha so‘rovlar yo‘q.', requestsLabel: 'so‘rov',
      recentRequestsTitle: 'So‘nggi xarid so‘rovlari', recentRequestsSubtitle: 'oxirgi 12 ta',
      tableCustomer: 'Mijoz', tablePhone: 'Telefon', tableProduct: 'Mahsulot', tableDate: 'Sana', tablePrice: 'Narx', tableStatus: 'Holat', tableViews: 'Ko‘rishlar',
      recentProductsTitle: 'Yaqinda qo‘shilgan mahsulotlar', openCatalog: 'Katalogni ochish',
      statusActive: 'Faol', statusInactive: 'Nofaol', statusFeatured: 'Tavsiya etilgan',
      dashboardFootnote: 'Bu sahifani faqat administratorlar ko‘ra oladi.',
      adminOnly: 'Statistikani faqat administrator ocha oladi.',
      // Admin bell & notifications
      notifications: 'Bildirishnomalar', unread: 'o‘qilmagan', allRead: 'Hammasi o‘qilgan', markAllRead: 'Hammasini o‘qilgan deb belgilash',
      noNotifications: 'Hozircha bildirishnoma yo‘q.', viewAllNotifications: 'Barcha bildirishnomalarni ko‘rish',
      notifToastTitle: 'Yangi bildirishnomalar', notifToastText: 'mijozlaringizdan yangi faollik', notifToastOpen: 'Ochish',
      notifLoginGoogle: 'Google orqali kirdi', notifLoginPassword: 'parol bilan kirdi',
      notifRegistered: 'akkaunt yaratdi', notifRegisteredLong: 'Saytda yangi akkaunt yaratti.',
      notifFavorited: 'sevimlilarga qo‘shdi', notifFavoritedLong: 'Pardani sevimlilarga qo‘shdi:',
      notifMessage: 'administratorga xabar yubordi', notifMessageLong: 'Administratorga xabar yubordi.',
      notifKindLogin: 'Kirishlar', notifKindRegister: 'Ro‘yxatdan o‘tishlar', notifKindFavorite: 'Sevimlilar', notifKindMessage: 'Xabarlar',
      filterUnread: 'O‘qilmagan', viaGoogle: 'Google orqali', viaPassword: 'parol orqali',
      // Users page
      users: 'Foydalanuvchilar', pageUsers: 'Foydalanuvchilar | SHTOR HOUSE', usersEyebrow: 'Auditoriya', usersTitle: 'Foydalanuvchilar',
      usersSubtitle: 'Har bir mijoz qanday kirganini, nimalarni sevimlilarga qo‘shganini ko‘ring va kerak bo‘lsa bloklang.',
      usersLive: 'Jonli auditoriya', usersFootnote: 'Faqat administratorlar foydalanuvchi faolligini ko‘ra oladi va bloklay oladi.',
      userJoined: 'Qo‘shilgan', userLastLogin: 'Oxirgi kirish', userSignIns: 'Kirishlar',
      userFavorites: 'Sevimlilar', userNoFavorites: 'Hozircha sevimli pardalar yo‘q.',
      userNeverSignedIn: 'Hali kirmagan', filterAll: 'Hammasi', filterGoogle: 'Google', filterPassword: 'Parol', filterBlocked: 'Bloklangan',
      blockedLabel: 'bloklangan', blockUser: 'Bloklash', blockUserConfirm: 'Ushbu foydalanuvchini bloklaysizmi? U tizimga kira olmaydi.',
      unblockUser: 'Blokdan chiqarish', unblockUserConfirm: 'Foydalanuvchini blokdan chiqarasizmi?',
      statAllUsers: 'Barcha foydalanuvchilar', statRegisteredAccounts: 'ro‘yxatdan o‘tgan hisoblar',
      statGoogleUsers: 'Google hisoblar', statGoogleLogins: 'Google kirishlari',
      statPasswordUsers: 'Parol hisoblar', statPasswordLogins: 'parol kirishlari',
      statBlockedUsers: 'Bloklangan', statBlockedHint: 'kira olmaydi',
      viewAllUsers: 'Barcha foydalanuvchilar',
      // Contact admin
      contactBackToProduct: 'Mahsulotga qaytish', adminContactEyebrow: 'To‘g‘ridan-to‘g‘ri xabar', adminContactTitle: 'Administratorga yozish',
      adminContactSubtitle: 'Savol bering, maxsus o‘lcham so‘rang yoki istagingizni yozing — xabar to‘g‘ridan-to‘g‘ri do‘kon administratoriga boradi.',
      adminContactFormTitle: 'Sizning xabaringiz', adminContactPrivate: 'Faqat administrator ko‘radi',
      msgFullName: 'Ismingiz', msgNamePlaceholder: 'To‘liq ismingiz', msgEmail: 'Email', msgEmailPlaceholder: 'siz@misol.uz',
      msgPhone: 'Telefon', msgPhonePlaceholder: '+998 90 123 45 67', msgText: 'Xabar', msgTextPlaceholder: 'Administratorga xabaringizni yozing…',
      phoneInvalid: '+998 dan keyin 9 ta raqam kiriting.',
      msgSend: 'Xabar yuborish', adminContactNote: 'Odatda bir ish kuni ichida javob beramiz.',
      pageContactAdmin: 'Administratorga xabar | SHTOR HOUSE',
      writeToAdmin: 'Administratorga yozish',
      // Notifications page
      notificationsEyebrow: 'Faollik lenti', notificationsTitle: 'Bildirishnomalar', notificationsSubtitle: 'Mijozlarning har bir kirishi, sevimlilari va xabarlari bitta joyda.',
      notificationsFootnote: 'Faqat administratorlar bu faollikni ko‘ra oladi.', notificationFilters: 'Bildirishnoma filtrlari',
      viewUser: 'Foydalanuvchini ko‘rish',
      // Product detail
      contactAbout: 'Mahsulot haqida bog‘lanish', contactText: 'Biz bilan bog‘lanish usulini tanlang, buyurtmangizni rasmiylashtirishga yordam beramiz.',
    },
    ru: {
      registerEyebrow: 'Добро пожаловать', registerTitle: 'Создать аккаунт', alreadyAccount: 'Уже есть аккаунт?', logIn: 'Войти',
      registeredUsers: 'зарегистрированных клиентов', featuredCurtains: 'Избранные шторы',
      curtainShowcaseEyebrow: 'Вдохновение для вашего дома',
      curtainShowcaseTitle: 'Выберите стиль для своего окна',
      curtainShowcaseHint: 'Шторы, жалюзи и другие решения для интерьера.',
      pauseShowcase: 'Остановить анимацию', resumeShowcase: 'Продолжить анимацию',
      heroEyebrow: 'Продуманные детали. Уютный дом.',
      heroTitle: 'Правильно подобранные шторы меняют атмосферу комнаты.',
      heroDescription: 'Выбирайте шторы и жалюзи по комнате, цвету и ткани и находите стиль для своего дома.',
      heroExplore: 'Смотреть коллекцию', heroContact: 'Связаться с нами',
      heroNote: 'Даже небольшая деталь помогает создать ваш неповторимый интерьер.',
      heroImageEyebrow: 'Ваш дом — ваш стиль', heroScroll: 'Найдите свой стиль',
      benefitsEyebrow: 'Для вашего образа жизни',
      benefitsTitle: 'Найти свой стиль должно быть легко.',
      benefitRoomTitle: 'Стиль для каждой комнаты',
      benefitRoomText: 'Идеи для гостиной, спальни, кухни и других комнат.',
      benefitSearchTitle: 'Выбирайте в своём темпе',
      benefitSearchText: 'Фильтруйте по категориям или ищите по цвету, ткани и стилю.',
      benefitFavoriteTitle: 'Сохраняйте понравившееся',
      benefitFavoriteText: 'Добавляйте шторы в избранное и возвращайтесь к ним в любое время.',
      featuredCollection: 'Выбор SHTOR HOUSE', featuredCurtainsTitle: 'Шторы, которые вдохновляют',
      previousCurtains: 'Предыдущие шторы', nextCurtains: 'Следующие шторы',
      pageSignIn: 'Войти | SHTOR HOUSE', pageRegister: 'Регистрация | SHTOR HOUSE', pageAddProduct: 'Добавить товар | SHTOR HOUSE',
      pageFavorites: 'Избранное | SHTOR HOUSE', pageReset: 'Сбросить пароль | SHTOR HOUSE', pageResetDone: 'Письмо отправлено | SHTOR HOUSE',
      pageResetConfirm: 'Новый пароль | SHTOR HOUSE', pageResetComplete: 'Пароль обновлен | SHTOR HOUSE',
      catalog: 'Каталог', share: 'Поделиться', inStock: 'В наличии', material: 'Материал:', length: 'Длина:', color: 'Цвет:',
      style: 'Стиль:', premiumLayered: 'Премиум, многослойный', favorite: '☆ В избранное', buy: 'Купить',
      purchase: 'Запрос на покупку', contactAbout: 'Свяжитесь с нами о товаре', contactText: 'Выберите удобный способ связи, и мы поможем оформить заказ.',
      deleteConfirm: 'Удалить этот товар без возможности восстановления?', footerTagline: 'Шторы для красивых пространств', locationLabel: 'Адрес', phoneLabel: 'Телефон',
      addImage: 'Скачать изображение', viewProduct: 'Посмотреть товар', removeFavorite: 'Убрать из избранного',
      welcomeRegister: 'Добро пожаловать', username: 'Имя пользователя', email: 'Электронная почта', newPassword: 'Новый пароль',
      confirmPassword: 'Подтвердите новый пароль', passwordHelp: 'Пароль должен содержать не менее 8 символов и не быть слишком простым.',
      accountRecovery: 'Восстановление аккаунта', resetTitle: 'Сбросить пароль', resetSubtitle: 'Введите email аккаунта, и мы отправим инструкции по сбросу пароля.',
      sendResetLink: 'Отправить ссылку', backSignIn: 'Вернуться ко входу', checkInbox: 'Проверьте почту', emailSent: 'Письмо отправлено',
      resetSentInfo: 'Если аккаунт с таким email существует, инструкции по сбросу отправлены.', allSet: 'Готово',
      passwordUpdated: 'Пароль обновлен', passwordUpdatedInfo: 'Ваш пароль успешно изменен.', signInNow: 'Войти',
      setNewPassword: 'Сохранить новый пароль', invalidResetLink: 'Ссылка для сброса пароля больше недействительна.', requestNewLink: 'Запросить новую ссылку',
      selectLanguage: 'Выберите язык', toggleTheme: 'Переключить светлую и темную тему', gridView: 'Сетка', listView: 'Список',
      sortProducts: 'Сортировать товары по названию', categoryFilters: 'Фильтры категорий', catalogView: 'Вид каталога', collectionGallery: 'Галерея коллекции',
      favoritesGallery: 'Галерея избранного', productActions: 'Действия с товаром', searchProducts: 'Поиск товаров', clearSearch: 'Очистить поиск',
      loginRequired: 'Войдите, чтобы сохранять избранное.', favoriteError: 'Не удалось обновить избранное. Попробуйте снова.',
      modalHelp: 'Мы поможем выбрать идеальные шторы для вашего пространства.', continue: 'Продолжить',
      modalSend: 'Расскажите о вашей комнате', modalRequest: 'Запросить консультацию по индивидуальному дизайну',
      modalDesign: 'Выберите стиль для интерьера', modalAlbums: 'Посмотрите коллекцию избранных штор',
      modalHelpTitle: 'Связаться со службой поддержки SHTOR HOUSE', close: 'Закрыть', tashkentUzbekistan: 'Ташкент, Узбекистан',
      openMap: 'Открыть карту',
      maintenanceLabel: 'Состояние сервиса', serviceUnavailableTitle: 'Произошла ошибка',
      serviceUnavailableMessage: 'Сервис Telegram сейчас недоступен. Мы работаем над исправлением.',
      accountCreated: 'Аккаунт успешно создан.',
      quoteSubmitted: 'Запрос успешно отправлен.',
      requestSent: 'Ваш запрос успешно отправлен.',
      productDeleted: 'Товар успешно удален.',
      staffDeleteOnly: 'Удалять товары может только администратор.',
      staffAddOnly: 'Добавлять товары может только администратор.',
      productAddedSuffix: 'успешно добавлен.',
      priceFilter: 'Цена ($)', priceFrom: 'от', priceTo: 'до', applyFilter: 'Фильтр', resetFilters: 'Сбросить',
      minPrice: 'Минимальная цена', maxPrice: 'Максимальная цена',
      sort_featured: 'Сначала рекомендуемые', sort_newest: 'Сначала новые', sort_price_asc: 'Цена: по возрастанию',
      sort_price_desc: 'Цена: по убыванию', sort_name_asc: 'Название: А–Я', sort_name_desc: 'Название: Я–А',
      dashboard: 'Статистика', pageDashboard: 'Статистика | SHTOR HOUSE', backToCatalog: 'Каталог',
      dashboardEyebrow: 'Панель администратора', dashboardTitle: 'Статистика сайта',
      dashboardSubtitle: 'Живая сводка посещений, товаров и запросов клиентов.',
      liveOverview: 'Онлайн-обзор', keyMetrics: 'Ключевые показатели',
      statVisits: 'Посещения сайта', statAllTime: 'за все время', statProducts: 'Товары', statActiveNow: 'активных',
      statRequests: 'Запросы на покупку', statLastSevenDays: 'за последние 7 дней', statUsers: 'Пользователи', statNewUsers: 'за 7 дней',
      statFavorites: 'Избранное', statSavedCurtains: 'сохраненных штор', statNewRequests: 'Новые запросы', statLastSevenDaysOnly: 'последние 7 дней',
      chartTitle: 'Запросы за последние 7 дней', chartSubtitle: 'Активность по дням', chartAria: 'Запросы по дням',
      chartEmpty: 'За последние 7 дней запросов нет.', categoryTitle: 'Товары по категориям', noProductsYet: 'Товаров пока нет.',
      topViewedTitle: 'Самые просматриваемые шторы', topViewedSubtitle: 'по просмотрам страниц', noViewsYet: 'Просмотров пока нет.', viewsLabel: 'просмотров',
      topRequestedTitle: 'Самые запрашиваемые шторы', topRequestedSubtitle: 'по запросам на покупку', noRequestsYet: 'Запросов пока нет.', requestsLabel: 'запросов',
      recentRequestsTitle: 'Последние запросы на покупку', recentRequestsSubtitle: 'последние 12',
      tableCustomer: 'Клиент', tablePhone: 'Телефон', tableProduct: 'Товар', tableDate: 'Дата', tablePrice: 'Цена', tableStatus: 'Статус', tableViews: 'Просмотры',
      recentProductsTitle: 'Недавно добавленные товары', openCatalog: 'Открыть каталог',
      statusActive: 'Активен', statusInactive: 'Неактивен', statusFeatured: 'Рекомендуемый',
      dashboardFootnote: 'Эту страницу видят только администраторы.',
      adminOnly: 'Статистику может открыть только администратор.',
      // Admin bell & notifications
      notifications: 'Уведомления', unread: 'непрочитанных', allRead: 'Все прочитано', markAllRead: 'Отметить все как прочитанные',
      noNotifications: 'Уведомлений пока нет.', viewAllNotifications: 'Посмотреть все уведомления',
      notifToastTitle: 'Новые уведомления', notifToastText: 'новая активность от ваших клиентов', notifToastOpen: 'Открыть',
      notifLoginGoogle: 'вошел через Google', notifLoginPassword: 'вошел по паролю',
      notifRegistered: 'создал аккаунт', notifRegisteredLong: 'Создал новый аккаунт на сайте.',
      notifFavorited: 'добавил в избранное', notifFavoritedLong: 'Добавил штору в избранное:',
      notifMessage: 'отправил сообщение администратору', notifMessageLong: 'Отправил сообщение администратору.',
      notifKindLogin: 'Входы', notifKindRegister: 'Регистрации', notifKindFavorite: 'Избранное', notifKindMessage: 'Сообщения',
      filterUnread: 'Непрочитанные', viaGoogle: 'через Google', viaPassword: 'по паролю',
      // Users page
      users: 'Пользователи', pageUsers: 'Пользователи | SHTOR HOUSE', usersEyebrow: 'Аудитория', usersTitle: 'Пользователи',
      usersSubtitle: 'Смотрите, как каждый клиент заходил, что добавил в избранное и блокируйте аккаунты при необходимости.',
      usersLive: 'Живая аудитория', usersFootnote: 'Только администраторы могут видеть активность пользователей и блокировать их.',
      userJoined: 'Зарегистрирован', userLastLogin: 'Последний вход', userSignIns: 'Входы',
      userFavorites: 'Избранное', userNoFavorites: 'Пока нет избранных штор.',
      userNeverSignedIn: 'Ещё не заходил', filterAll: 'Все', filterGoogle: 'Google', filterPassword: 'Пароль', filterBlocked: 'Заблокированные',
      blockedLabel: 'заблокирован', blockUser: 'Заблокировать', blockUserConfirm: 'Заблокировать этого пользователя? Он не сможет зайти.',
      unblockUser: 'Разблокировать', unblockUserConfirm: 'Разблокировать этого пользователя?',
      statAllUsers: 'Все пользователи', statRegisteredAccounts: 'зарегистрированных аккаунтов',
      statGoogleUsers: 'Google-аккаунты', statGoogleLogins: 'входов через Google',
      statPasswordUsers: 'Аккаунты с паролем', statPasswordLogins: 'входов по паролю',
      statBlockedUsers: 'Заблокированные', statBlockedHint: 'не могут зайти',
      viewAllUsers: 'Все пользователи',
      // Contact admin
      contactBackToProduct: 'Назад к товару', adminContactEyebrow: 'Прямое сообщение', adminContactTitle: 'Написать администратору',
      adminContactSubtitle: 'Задайте вопрос, запросите индивидуальный размер или поделитесь пожеланием — сообщение попадёт прямо администратору магазина.',
      adminContactFormTitle: 'Ваше сообщение', adminContactPrivate: 'Видит только администратор',
      msgFullName: 'Ваше имя', msgNamePlaceholder: 'Полное имя', msgEmail: 'Email', msgEmailPlaceholder: 'you@example.com',
      msgPhone: 'Телефон', msgPhonePlaceholder: '+998 90 123 45 67', msgText: 'Сообщение', msgTextPlaceholder: 'Напишите сообщение администратору…',
      phoneInvalid: 'Введите ровно 9 цифр после +998.',
      msgSend: 'Отправить', adminContactNote: 'Обычно отвечаем в течение одного рабочего дня.',
      pageContactAdmin: 'Сообщение администратору | SHTOR HOUSE',
      writeToAdmin: 'Написать администратору',
      // Notifications page
      notificationsEyebrow: 'Лента активности', notificationsTitle: 'Уведомления', notificationsSubtitle: 'Каждый вход, избранное и сообщение от ваших клиентов — в одном месте.',
      notificationsFootnote: 'Только администраторы видят эту активность.', notificationFilters: 'Фильтры уведомлений',
      viewUser: 'Посмотреть пользователя',
      // Product detail
      contactAbout: 'Свяжитесь с нами о товаре', contactText: 'Выберите удобный способ связи, и мы поможем оформить заказ.',
    }
  };
  Object.keys(extraTranslations).forEach(function (language) {
    Object.assign(translations[language], extraTranslations[language]);
  });
  const validationTranslations = {
    'Please enter a correct username and password. Note that both fields may be case-sensitive.': {
      en: 'Please enter a correct username and password. Note that both fields may be case-sensitive.',
      uz: 'Foydalanuvchi nomi va parolni to‘g‘ri kiriting. Katta-kichik harflar farqlanadi.',
      ru: 'Введите правильные имя пользователя и пароль. Учитывается регистр букв.'
    },
    'The two password fields didn’t match.': {
      en: 'The two password fields didn’t match.',
      uz: 'Kiritilgan parollar bir-biriga mos kelmadi.',
      ru: 'Введенные пароли не совпадают.'
    },
    'This password is too short. It must contain at least 8 characters.': {
      en: 'This password is too short. It must contain at least 8 characters.',
      uz: 'Parol juda qisqa. Kamida 8 ta belgidan iborat bo‘lishi kerak.',
      ru: 'Пароль слишком короткий. Он должен содержать не менее 8 символов.'
    },
    'This password is too common.': {
      en: 'This password is too common.',
      uz: 'Bu parol juda oddiy.',
      ru: 'Этот пароль слишком распространенный.'
    },
    'This password is entirely numeric.': {
      en: 'This password is entirely numeric.',
      uz: 'Parol faqat raqamlardan iborat bo‘lmasligi kerak.',
      ru: 'Пароль не должен состоять только из цифр.'
    },
    'The password is too similar to the username.': {
      en: 'The password is too similar to the username.',
      uz: 'Parol foydalanuvchi nomiga juda o‘xshash.',
      ru: 'Пароль слишком похож на имя пользователя.'
    },
    'Enter a valid email address.': {
      en: 'Enter a valid email address.',
      uz: 'To‘g‘ri email manzilini kiriting.',
      ru: 'Введите корректный адрес электронной почты.'
    },
    'This field is required.': {
      en: 'This field is required.',
      uz: 'Bu maydonni to‘ldirish shart.',
      ru: 'Это поле обязательно для заполнения.'
    },
    'A user with that username already exists.': {
      en: 'A user with that username already exists.',
      uz: 'Bu foydalanuvchi nomi band.',
      ru: 'Пользователь с таким именем уже существует.'
    },
    'Upload a valid JPG, PNG, or WEBP image.': {
      en: 'Upload a valid JPG, PNG, or WEBP image.',
      uz: 'JPG, PNG, WEBP yoki HEIC formatidagi to‘g‘ri rasmni yuklang.',
      ru: 'Загрузите корректное изображение в формате JPG, PNG, WEBP или HEIC.'
    }
  };

  const passwordVisibilityTranslations = {
    en: { showPassword: 'Show password', hidePassword: 'Hide password' },
    uz: { showPassword: 'Parolni ko‘rsatish', hidePassword: 'Parolni yashirish' },
    ru: { showPassword: 'Показать пароль', hidePassword: 'Скрыть пароль' }
  };
  let currentLanguage = 'en';

  function setLanguage(language) {
    currentLanguage = passwordVisibilityTranslations[language] ? language : 'en';
    const copy = Object.assign(
      {},
      translations[currentLanguage] || translations.en,
      passwordVisibilityTranslations[currentLanguage]
    );
    document.documentElement.lang = language;
    document.querySelectorAll('[data-i18n]').forEach(function (element) {
      if (copy[element.dataset.i18n]) element.textContent = copy[element.dataset.i18n];
    });
    document.querySelectorAll('[data-i18n-placeholder]').forEach(function (element) {
      if (copy[element.dataset.i18nPlaceholder]) element.placeholder = copy[element.dataset.i18nPlaceholder];
    });
    document.querySelectorAll('[data-i18n-title]').forEach(function (element) {
      if (copy[element.dataset.i18nTitle]) element.title = copy[element.dataset.i18nTitle];
    });
    document.querySelectorAll('[data-i18n-aria-label]').forEach(function (element) {
      if (copy[element.dataset.i18nAriaLabel]) element.setAttribute('aria-label', copy[element.dataset.i18nAriaLabel]);
    });
    document.querySelectorAll('[data-category]').forEach(function (element) {
      element.textContent = copy['category_' + element.dataset.category] || element.dataset.category;
    });
    const messageTranslations = {
      'Google sign-in is not configured yet.': copy.googleNotConfigured,
      'Google sign-in session expired. Please try again.': copy.googleSessionExpired,
      'Google sign-in was cancelled.': copy.googleCancelled,
      'Google sign-in could not be completed.': copy.googleFailed,
      'Google did not provide a verified email address.': copy.googleEmailFailed,
      'Account created successfully.': copy.accountCreated,
      'Your quote request has been submitted successfully.': copy.quoteSubmitted,
      'Your request has been sent successfully.': copy.requestSent,
      'Product deleted successfully.': copy.productDeleted,
      'Only an administrator can delete products.': copy.staffDeleteOnly,
      'Only an administrator can add products.': copy.staffAddOnly,
      'Only an administrator can open the dashboard.': copy.adminOnly
    };
    document.querySelectorAll('.message').forEach(function (element) {
      const message = element.textContent.trim();
      if (messageTranslations[message]) {
        element.textContent = messageTranslations[message];
      } else if (message.endsWith(' was added successfully.')) {
        element.textContent = message.slice(0, -' was added successfully.'.length) + ' ' + copy.productAddedSuffix;
      }
    });
    document.querySelectorAll('.field-errors li, .form-error li').forEach(function (element) {
      const error = element.textContent.trim();
      if (validationTranslations[error]) element.textContent = validationTranslations[error][language] || error;
    });
    const pageTitle = document.querySelector('[data-page-title]');
    if (pageTitle && copy[pageTitle.dataset.pageTitle]) document.title = copy[pageTitle.dataset.pageTitle];
    document.querySelectorAll('label[data-field-name]').forEach(function (label) {
      const fieldNames = {
        username: 'username', email: 'email', password1: 'password', password2: 'confirmPassword',
        new_password1: 'newPassword', new_password2: 'confirmPassword'
      };
      const translationKey = fieldNames[label.dataset.fieldName];
      if (translationKey && copy[translationKey]) label.textContent = copy[translationKey];
    });
    const placeholders = {
      username: { en: 'Email or username', uz: 'Email yoki foydalanuvchi nomi', ru: 'Email или имя пользователя' },
      name: { en: 'Luxury curtain name', uz: 'Parda nomi', ru: 'Название шторы' },
      material: { en: 'Silk, linen, cotton', uz: 'Ipak, zig‘ir, paxta', ru: 'Шелк, лен, хлопок' },
      origin: { en: 'For example: Turkey', uz: 'Masalan: Turkiya', ru: 'Например: Турция' },
      color: { en: 'Ivory, sand, beige', uz: 'Fil suyagi, qum, bej', ru: 'Айвори, песочный, бежевый' },
      length_meters: { en: 'For example: 3.50', uz: 'Masalan: 3,50', ru: 'Например: 3,50' },
      description: { en: 'Describe the curtain and its benefits', uz: 'Parda va uning afzalliklarini yozing', ru: 'Опишите штору и ее преимущества' }
    };
    Object.keys(placeholders).forEach(function (field) {
      const input = document.getElementById('id_' + field);
      if (!input) return;
      if (field === 'username' && !document.querySelector('[data-page-title="pageSignIn"]')) {
        input.placeholder = copy.username;
      } else {
        input.placeholder = placeholders[field][language] || placeholders[field].en;
      }
    });
    const categorySelect = document.getElementById('id_category');
    if (categorySelect) Array.from(categorySelect.options).forEach(function (option) { option.textContent = copy['category_' + option.value] || option.textContent; });
    localStorage.setItem('parda-language', language);
  }
  if (languageSelect) {
    languageSelect.value = localStorage.getItem('parda-language') || 'en';
    setLanguage(languageSelect.value);
    languageSelect.addEventListener('change', function () { setLanguage(languageSelect.value); });
  } else setLanguage(localStorage.getItem('parda-language') || 'en');
  document.querySelectorAll('[data-language-picker]').forEach(function (picker) {
    const select = picker.querySelector('.language-picker-native');
    const trigger = picker.querySelector('[data-language-trigger]');
    const currentLabel = picker.querySelector('[data-language-current]');
    const menu = picker.querySelector('[data-language-menu]');
    const options = Array.from(picker.querySelectorAll('[data-language-option]'));
    if (!select || !trigger || !currentLabel || !menu) return;

    function syncLanguagePicker() {
      const selectedOption = select.options[select.selectedIndex];
      if (selectedOption) currentLabel.textContent = selectedOption.textContent;
      options.forEach(function (option) {
        option.setAttribute('aria-selected', String(option.dataset.languageOption === select.value));
      });
    }

    function closeLanguageMenu(restoreFocus) {
      menu.hidden = true;
      trigger.setAttribute('aria-expanded', 'false');
      if (restoreFocus) trigger.focus();
    }

    function openLanguageMenu(focusSelected) {
      menu.hidden = false;
      trigger.setAttribute('aria-expanded', 'true');
      if (focusSelected) {
        const selectedOption = options.find(function (option) {
          return option.dataset.languageOption === select.value;
        });
        (selectedOption || options[0])?.focus();
      }
    }

    trigger.addEventListener('click', function () {
      if (menu.hidden) openLanguageMenu(false);
      else closeLanguageMenu(false);
    });
    trigger.addEventListener('keydown', function (event) {
      if (event.key === 'ArrowDown' || event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        openLanguageMenu(true);
      } else if (event.key === 'ArrowUp') {
        event.preventDefault();
        openLanguageMenu(true);
        options[options.length - 1]?.focus();
      } else if (event.key === 'Escape' && !menu.hidden) {
        event.preventDefault();
        closeLanguageMenu(false);
      }
    });
    menu.addEventListener('click', function (event) {
      const option = event.target.closest('[data-language-option]');
      if (!option) return;
      select.value = option.dataset.languageOption;
      select.dispatchEvent(new Event('change', { bubbles: true }));
      syncLanguagePicker();
      closeLanguageMenu(true);
    });
    menu.addEventListener('keydown', function (event) {
      const currentIndex = options.indexOf(document.activeElement);
      let nextIndex = currentIndex;
      if (event.key === 'ArrowDown') nextIndex = (currentIndex + 1) % options.length;
      else if (event.key === 'ArrowUp') nextIndex = (currentIndex - 1 + options.length) % options.length;
      else if (event.key === 'Home') nextIndex = 0;
      else if (event.key === 'End') nextIndex = options.length - 1;
      else if (event.key === 'Escape') {
        event.preventDefault();
        closeLanguageMenu(true);
        return;
      } else if (event.key === 'Tab') {
        closeLanguageMenu(false);
        return;
      } else return;
      event.preventDefault();
      options[nextIndex]?.focus();
    });
    select.addEventListener('change', syncLanguagePicker);
    document.addEventListener('pointerdown', function (event) {
      if (!picker.contains(event.target) && !menu.hidden) closeLanguageMenu(false);
    }, { signal: pageSignal });
    syncLanguagePicker();
  });
  const ticker = document.querySelector('[data-curtain-ticker]');
  const tickerToggle = document.querySelector('[data-ticker-toggle]');
  if (ticker && tickerToggle) {
    const pointerPause = function () { ticker.classList.add('is-pointer-paused'); };
    const pointerResume = function () { ticker.classList.remove('is-pointer-paused'); };

    ticker.addEventListener('pointerdown', function (event) {
      if (event.pointerType === 'mouse') pointerPause();
    });
    window.addEventListener('pointerup', pointerResume, { signal: pageSignal });
    window.addEventListener('pointercancel', pointerResume, { signal: pageSignal });
    tickerToggle.addEventListener('click', function () {
      const paused = ticker.classList.toggle('is-paused');
      tickerToggle.setAttribute('aria-pressed', String(paused));
      const copy = translations[currentLanguage] || translations.en;
      tickerToggle.textContent = paused ? copy.resumeShowcase : copy.pauseShowcase;
    });
  }
  const revealTargets = document.querySelectorAll('[data-reveal], [data-reveal-item]');
  const reducedMotionPreference = window.matchMedia('(prefers-reduced-motion: reduce)');
  if (revealTargets.length && 'IntersectionObserver' in window && !reducedMotionPreference.matches) {
    document.body.classList.add('has-scroll-reveal');
    const revealObserver = new IntersectionObserver(function (entries, observer) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add('is-visible');
          observer.unobserve(entry.target);
        }
      });
    }, { threshold: 0.12 });
    revealTargets.forEach(function (element) { revealObserver.observe(element); });
  }
  const promoTrack = document.querySelector('[data-promo-track]');
  if (promoTrack) {
    const promoSlides = Array.from(promoTrack.querySelectorAll('.promo-slide'));
    const previousButton = document.querySelector('[data-promo-prev]');
    const nextButton = document.querySelector('[data-promo-next]');
    const positionLabel = document.querySelector('[data-promo-position]');
    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
    let activePromoIndex = 0;
    let promoTimer;

    function updatePromoPosition() {
      const gap = Number.parseFloat(window.getComputedStyle(promoTrack).gap) || 0;
      const slideWidth = promoSlides[0]?.getBoundingClientRect().width || 0;
      const step = slideWidth + gap;
      if (step > 0) activePromoIndex = Math.min(
        promoSlides.length - 1,
        Math.max(0, Math.round(promoTrack.scrollLeft / step))
      );
      if (positionLabel) {
        positionLabel.textContent =
          String(activePromoIndex + 1).padStart(2, '0') +
          ' / ' +
          String(promoSlides.length).padStart(2, '0');
      }
    }

    function movePromo(direction) {
      if (promoSlides.length < 2) return;
      updatePromoPosition();
      activePromoIndex = (activePromoIndex + direction + promoSlides.length) % promoSlides.length;
      promoSlides[activePromoIndex].scrollIntoView({
        behavior: reducedMotion.matches ? 'auto' : 'smooth',
        block: 'nearest',
        inline: 'start'
      });
      if (positionLabel) {
        positionLabel.textContent =
          String(activePromoIndex + 1).padStart(2, '0') +
          ' / ' +
          String(promoSlides.length).padStart(2, '0');
      }
    }

    function stopPromoAutoplay() {
      window.clearInterval(promoTimer);
    }

    function startPromoAutoplay() {
      stopPromoAutoplay();
      if (
        promoSlides.length > 1 &&
        !reducedMotion.matches &&
        document.visibilityState === 'visible'
      ) {
        promoTimer = window.setInterval(function () { movePromo(1); }, 5000);
      }
    }

    previousButton?.addEventListener('click', function () { movePromo(-1); });
    nextButton?.addEventListener('click', function () { movePromo(1); });
    if (previousButton) previousButton.disabled = promoSlides.length < 2;
    if (nextButton) nextButton.disabled = promoSlides.length < 2;
    promoTrack.addEventListener('scroll', updatePromoPosition, { passive: true });
    promoTrack.addEventListener('pointerenter', stopPromoAutoplay);
    promoTrack.addEventListener('pointerleave', startPromoAutoplay);
    promoTrack.addEventListener('focusin', stopPromoAutoplay);
    promoTrack.addEventListener('focusout', function (event) {
      if (!promoTrack.contains(event.relatedTarget)) startPromoAutoplay();
    });
    document.addEventListener('visibilitychange', startPromoAutoplay, { signal: pageSignal });
    reducedMotion.addEventListener('change', startPromoAutoplay);
    window.addEventListener('resize', updatePromoPosition, { signal: pageSignal });
    updatePromoPosition();
    startPromoAutoplay();
  }
  document.querySelectorAll('[data-password-toggle]').forEach(function (button) {
    const passwordInput = button.closest('.password-input-wrap')?.querySelector('input');
    if (!passwordInput) return;

    button.addEventListener('click', function () {
      const isVisible = passwordInput.type === 'password';
      passwordInput.type = isVisible ? 'text' : 'password';
      button.setAttribute('aria-pressed', String(isVisible));
      button.dataset.i18nAriaLabel = isVisible ? 'hidePassword' : 'showPassword';
      const copy = passwordVisibilityTranslations[currentLanguage];
      button.setAttribute('aria-label', copy[button.dataset.i18nAriaLabel]);
    });
  });
  document.querySelectorAll('form[data-confirm-i18n]').forEach(function (form) {
    form.addEventListener('submit', function (event) {
      const language = localStorage.getItem('parda-language') || 'en';
      const copy = translations[language] || translations.en;
      if (!window.confirm(copy[form.dataset.confirmI18n] || 'Are you sure?')) event.preventDefault();
    });
  });
  const googleLogin = document.querySelector('[data-google-login]');
  const googleNote = document.querySelector('[data-google-note]');
  if (googleLogin && googleNote) googleLogin.addEventListener('click', function () { googleNote.hidden = false; });
  if (profileToggle && profileMenu) {
    profileToggle.addEventListener('click', function () {
      const isOpen = profileMenu.classList.toggle('open');
      profileToggle.setAttribute('aria-expanded', String(isOpen));
    });
    document.addEventListener('click', function (event) {
      if (!profileToggle.contains(event.target) && !profileMenu.contains(event.target)) profileMenu.classList.remove('open');
    }, { signal: pageSignal });
  }

  // =========================================================
  // ADMIN BELL NOTIFICATIONS — administrator bildirishnomalari
  // =========================================================
  const adminBell = document.querySelector('[data-admin-bell]');
  if (adminBell) {
    const trigger = adminBell.querySelector('[data-admin-bell-toggle]');
    const menu = adminBell.querySelector('[data-admin-bell-menu]');
    const badge = adminBell.querySelector('[data-admin-bell-badge]');

    // Panelni ekran chetidan chiqmaydigan qilib joylashtirish
    function positionBellMenu() {
      if (!menu || !trigger) return;
      const rect = trigger.getBoundingClientRect();
      const anchor = adminBell.getBoundingClientRect();
      const vw = window.innerWidth || document.documentElement.clientWidth;
      const vh = window.innerHeight || document.documentElement.clientHeight;
      const margin = 8;
      const width = Math.min(380, vw - margin * 2);
      let left = rect.right - width;
      left = Math.max(margin, Math.min(left, vw - width - margin));
      const top = rect.bottom + 8;
      menu.style.width = width + 'px';
      menu.style.left = (left - anchor.left) + 'px';
      menu.style.right = 'auto';
      menu.style.top = (rect.bottom - anchor.top + 8) + 'px';
      menu.style.maxHeight = Math.max(220, vh - top - margin) + 'px';
      const list = menu.querySelector('.admin-bell-list');
      if (list) list.style.maxHeight = Math.max(120, vh - top - margin - 118) + 'px';
    }

    if (trigger) {
      trigger.addEventListener('click', function (event) {
        event.stopPropagation();
        const isOpen = adminBell.classList.toggle('open');
        trigger.setAttribute('aria-expanded', String(isOpen));
        if (isOpen) {
          // Bell ochilganda badjeni "o'qilgan" holatiga o'tkazish
          positionBellMenu();
          adminBell.classList.add('has-open');
          if (badge) badge.classList.remove('badge-pulse');
        }
      });

      document.addEventListener('click', function (event) {
        if (!adminBell.contains(event.target)) {
          adminBell.classList.remove('open');
          trigger.setAttribute('aria-expanded', 'false');
        }
      }, { signal: pageSignal });

      document.addEventListener('keydown', function (event) {
        if (event.key === 'Escape' && adminBell.classList.contains('open')) {
          adminBell.classList.remove('open');
          trigger.setAttribute('aria-expanded', 'false');
          trigger.focus();
        }
      }, { signal: pageSignal });

      window.addEventListener('resize', function () {
        if (adminBell.classList.contains('open')) positionBellMenu();
      }, { signal: pageSignal });
    }

    // Badge puls animatsiyasi (yangi xabar keldigida)
    function animateBellBadge() {
      if (badge && !adminBell.classList.contains('open')) {
        badge.classList.add('badge-pulse');
        setTimeout(function () { badge.classList.remove('badge-pulse'); }, 600);
      }
    }

    // Agar sahifa yuklanganda o'qilmagan bildirishnomalar bo'lsa, badjeni animatsiya qil
    if (badge) {
      setTimeout(animateBellBadge, 500);
    }
  }

  // Toast bildirishnoma (yangi xabar keldigida animatsiya bilan ko'rsatish)
  const toast = document.querySelector('[data-admin-toast]');
  if (toast) {
    const closeBtn = toast.querySelector('[data-admin-toast-close]');
    const link = toast.querySelector('[data-admin-toast-link]');

    // Avtomatik yashirish 8 sekunddan keyin
    setTimeout(function () {
      if (!toast.hidden && !toast.classList.contains('toast-hiding')) {
        hideToast();
      }
    }, 8000);

    function hideToast() {
      toast.classList.add('toast-hiding');
      toast.addEventListener('transitionend', function () {
        toast.hidden = true;
      }, { once: true });
    }

    if (closeBtn) {
      closeBtn.addEventListener('click', function (event) {
        event.stopPropagation();
        hideToast();
      });
    }

    // Toast ustiga bosilganda ham yashirish (linkdan tashqari)
    toast.addEventListener('click', function (event) {
      if (event.target === toast || event.target.closest('.admin-toast-copy')) {
        window.location.href = link.href;
      } else if (event.target !== link && !event.target.closest('[data-admin-toast-close]')) {
        hideToast();
      }
    });
  }

  // =========================================================
  // ADMIN CONTACT — telefon raqami: +998 prefiksi, faqat raqamlar
  // =========================================================
  document.querySelectorAll('[data-phone-input]').forEach(function (input) {
    const form = input.closest('form');
    const error = form ? form.querySelector('[data-phone-error]') : null;
    const PREFIX = '+998';

    function digitsFrom(value) {
      let digits = String(value || '').replace(/\D/g, '');
      while (digits.indexOf('998') === 0) digits = digits.slice(3);
      return digits.slice(0, 9);
    }

    function formatPhone(digits) {
      let out = PREFIX;
      if (digits.length) out += ' ' + digits.slice(0, 2);
      if (digits.length > 2) out += ' ' + digits.slice(2, 5);
      if (digits.length > 5) out += ' ' + digits.slice(5, 7);
      if (digits.length > 7) out += ' ' + digits.slice(7, 9);
      return out;
    }

    function showPhoneError(show) {
      if (error) {
        error.hidden = !show;
        if (show) {
          const copy = translations[currentLanguage] || translations.en;
          error.textContent = copy.phoneInvalid || translations.en.phoneInvalid;
        }
      }
      input.classList.toggle('is-invalid', show);
      input.setAttribute('aria-invalid', show ? 'true' : 'false');
    }

    input.value = digitsFrom(input.value) ? formatPhone(digitsFrom(input.value)) : '';

    input.addEventListener('focus', function () {
      if (!digitsFrom(input.value)) input.value = PREFIX + ' ';
      input.setSelectionRange(input.value.length, input.value.length);
    });

    input.addEventListener('keydown', function (event) {
      if (event.ctrlKey || event.metaKey || event.altKey) return;
      if (event.key.length === 1 && !/[0-9]/.test(event.key)) {
        event.preventDefault();
        return;
      }
      if ((event.key === 'Backspace' || event.key === 'Delete')
        && input.selectionStart <= PREFIX.length && input.selectionEnd <= PREFIX.length) {
        event.preventDefault();
      }
    });

    input.addEventListener('input', function () {
      const digits = digitsFrom(input.value);
      input.value = formatPhone(digits);
      input.setSelectionRange(input.value.length, input.value.length);
      if (digits.length === 9) showPhoneError(false);
    });

    input.addEventListener('blur', function () {
      const digits = digitsFrom(input.value);
      if (!digits.length) {
        input.value = '';
        showPhoneError(false);
        return;
      }
      input.value = formatPhone(digits);
      showPhoneError(digits.length !== 9);
    });

    if (form) {
      form.addEventListener('submit', function (event) {
        const digits = digitsFrom(input.value);
        if (!digits.length) {
          input.value = '';
          showPhoneError(false);
          return;
        }
        if (digits.length !== 9) {
          event.preventDefault();
          showPhoneError(true);
          input.focus();
          return;
        }
        input.value = PREFIX + digits;
        showPhoneError(false);
      });
    }
  });

  // =========================================================
  // MAHSULOT KARTASI — butun karta bosilganda mahsulot ochiladi
  // =========================================================
  document.querySelectorAll('.gallery-card').forEach(function (card) {
    const link = card.querySelector('a.card-link');
    if (!link) return;
    card.addEventListener('click', function (event) {
      if (event.target.closest('a, button, [data-favorite-slug], [data-download-image]')) return;
      const href = link.getAttribute('href');
      if (href) window.location.href = href;
    });
  });

  const quoteSection = document.getElementById('quote-form');
  document.querySelectorAll('[data-scroll="quote-form"]').forEach(function (button) { button.addEventListener('click', function () { quoteSection?.scrollIntoView({ behavior: 'smooth' }); }); });
  document.querySelectorAll('[data-action]').forEach(function (button) {
    button.addEventListener('click', function () {
      const action = button.dataset.action;
      const targets = { send: '#quote-form', request: '#quote-form', showcase: '.gallery-grid', design: '#features', albums: '.featured-section', help: '#resources' };
      if (targets[action]) document.querySelector(targets[action])?.scrollIntoView({ behavior: 'smooth' });
      if (action === 'collapse') document.querySelector('.sidebar')?.classList.toggle('collapsed');
      if (action === 'close-preview') button.closest('.preview-tag').style.display = 'none';
      if (['send', 'request', 'design', 'albums', 'help'].includes(action)) openInfoModal(action);
    });
  });
  document.querySelectorAll('[data-view]').forEach(function (button) { button.addEventListener('click', function () { gallery?.classList.toggle('list-view', button.dataset.view === 'list'); document.querySelectorAll('[data-view]').forEach(function (item) { item.classList.toggle('active', item === button); }); }); });

  // Saralash o'zgarganda filtr formasi avtomatik yuboriladi.
  // Bo'sh narx maydonlari va standart saralash URL ga qo'shilmaydi.
  function cleanCatalogForm(form) {
    form.querySelectorAll('input[name="min_price"], input[name="max_price"]').forEach(function (input) {
      if (!input.value.trim()) input.disabled = true;
    });
    const sortField = form.querySelector('select[name="sort"]');
    if (sortField && sortField.value === 'featured') sortField.disabled = true;
  }

  document.querySelectorAll('.catalog-filters').forEach(function (form) {
    form.addEventListener('submit', function () { cleanCatalogForm(form); });
    form.querySelectorAll('[data-auto-submit]').forEach(function (field) {
      field.addEventListener('change', function () {
        cleanCatalogForm(form);
        form.submit();
      });
    });
  });

  const themeButtons = document.querySelectorAll('.theme-toggle');
  function setTheme(theme) { document.body.classList.toggle('light-mode', theme === 'light'); themeButtons.forEach(function (button) { button.textContent = theme === 'light' ? '☾' : '☼'; }); localStorage.setItem('parda-theme', theme); }
  setTheme(localStorage.getItem('parda-theme') || 'dark');
  themeButtons.forEach(function (button) { button.addEventListener('click', function () { setTheme(document.body.classList.contains('light-mode') ? 'dark' : 'light'); }); });

  // =========================================================
  // FAVORITES (Sevimlilar) — serverga AJAX orqali saqlanadi
  // =========================================================
  function getCookie(name) {
    const match = document.cookie.match(new RegExp('(^|;\\s*)' + name + '\\s*=\\s*([^;]+)'));
    return match ? decodeURIComponent(match[2]) : null;
  }
  const csrfToken = (document.querySelector('meta[name="csrf-token"]') || {}).content || getCookie('csrftoken');

  function updateFavoriteCount(count) {
    document.querySelectorAll('[data-favorites-count]').forEach(function (el) { el.textContent = count; });
  }

  document.querySelectorAll('[data-favorite-slug]').forEach(function (button) {
    button.addEventListener('click', function (event) {
      event.preventDefault();
      const slug = button.dataset.favoriteSlug;
      button.disabled = true;
      fetch('/favorite/' + slug + '/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'X-Requested-With': 'XMLHttpRequest',
        },
      })
        .then(function (response) {
          if (response.status === 401) {
            window.location.href = '/login/?next=' + encodeURIComponent(window.location.pathname + window.location.search);
            return null;
          }
          return response.json();
        })
        .then(function (data) {
          if (!data) return;
          if (data.ok) {
            button.classList.toggle('selected', data.is_favorite);
            button.textContent = data.is_favorite ? '★' : '☆';
            updateFavoriteCount(data.count);
            if (window.location.pathname === '/wishlist/' && !data.is_favorite) {
              const card = button.closest('.gallery-card');
              if (card) card.remove();
            }
          }
        })
        .catch(function () { /* tarmoq xatosi — jim o'tish */ })
        .finally(function () { button.disabled = false; });
    });
  });
  document.querySelectorAll('[data-download-image]').forEach(function (button) {
    button.addEventListener('click', function () {
      const link = document.createElement('a');
      link.href = button.dataset.downloadImage;
      link.download = (button.dataset.downloadName || 'parda-image') + '.jpg';
      link.target = '_blank';
      link.rel = 'noopener';
      link.click();
    });
  });
  const modal = document.querySelector('[data-modal]');
  document.querySelectorAll('[data-buy]').forEach(function (button) { button.addEventListener('click', function () { if (modal) modal.hidden = false; }); });
  document.querySelectorAll('[data-modal-close]').forEach(function (button) { button.addEventListener('click', function () { if (modal) modal.hidden = true; }); });
  if (modal) modal.addEventListener('click', function (event) { if (event.target === modal) modal.hidden = true; });
  const maintenanceModal = document.querySelector('[data-maintenance-modal]');
  let maintenanceTrigger = null;
  document.querySelectorAll('[data-maintenance-trigger]').forEach(function (trigger) {
    trigger.addEventListener('click', function (event) {
      event.preventDefault();
      maintenanceTrigger = trigger;
      if (!maintenanceModal) return;
      maintenanceModal.hidden = false;
      maintenanceModal.querySelector('[data-maintenance-close]').focus();
    });
  });
  function closeMaintenanceModal() {
    if (!maintenanceModal || maintenanceModal.hidden) return;
    maintenanceModal.hidden = true;
    if (maintenanceTrigger) maintenanceTrigger.focus();
  }
  document.querySelectorAll('[data-maintenance-close]').forEach(function (button) {
    button.addEventListener('click', closeMaintenanceModal);
  });
  if (maintenanceModal) {
    maintenanceModal.addEventListener('click', function (event) {
      if (event.target === maintenanceModal) closeMaintenanceModal();
    });
    document.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') closeMaintenanceModal();
    }, { signal: pageSignal });
  }
  document.querySelectorAll('[data-share]').forEach(function (button) { button.addEventListener('click', function () { if (navigator.share) navigator.share({ title: document.title, url: window.location.href }); else navigator.clipboard.writeText(window.location.href); }); });

  function openInfoModal(action) {
    const copy = translations[localStorage.getItem('parda-language') || 'en'] || translations.en;
    const messages = { send: copy.modalSend, request: copy.modalRequest, design: copy.modalDesign, albums: copy.modalAlbums, help: copy.modalHelpTitle };
    const modalBox = document.createElement('div');
    modalBox.className = 'modal-backdrop';
    modalBox.innerHTML = '<div class="contact-modal" role="dialog"><button class="modal-close" type="button" aria-label="' + copy.selectLanguage + '">×</button><p class="eyebrow">SHTOR HOUSE</p><h2>' + messages[action] + '</h2><p>' + copy.modalHelp + '</p><a class="btn btn-primary" href="tel:+998974244242">' + copy.continue + '</a></div>';
    document.body.appendChild(modalBox);
    modalBox.querySelector('.modal-close').addEventListener('click', function () { modalBox.remove(); });
  }

  /* =========================================================
     CONTENT PROTECTION — matn belgilash va nusxalashni bloklash
     Forma maydonlari (input, textarea, select) va tahrirlanadigan
     joylar chetlab o'tiladi, aks holda formalar ishlamay qoladi.
     ========================================================= */
  function isEditable(target) {
    if (!target) return false;
    const tag = target.tagName;
    return tag === 'INPUT' || tag === 'TEXTAREA' || tag === 'SELECT' || target.isContentEditable;
  }

  // 1) Matn belgilashni (selection) bloklash
  document.addEventListener('selectstart', function (event) {
    if (!isEditable(event.target)) event.preventDefault();
  }, { signal: pageSignal });

  // 2) Nusxalash, kesish va qo'yishni bloklash
  ['copy', 'cut'].forEach(function (type) {
    document.addEventListener(type, function (event) {
      if (!isEditable(event.target)) event.preventDefault();
    }, { signal: pageSignal });
  });

  // 3) O'ng tugma menyusini bloklash
  document.addEventListener('contextmenu', function (event) {
    if (!isEditable(event.target)) event.preventDefault();
  }, { signal: pageSignal });

  // 4) Ctrl/Cmd + C, X, A, S, U, P klavishalarini bloklash
  document.addEventListener('keydown', function (event) {
    if (!(event.ctrlKey || event.metaKey)) return;
    if (isEditable(event.target)) return;
    const blocked = ['c', 'C', 'x', 'X', 'a', 'A', 's', 'S', 'u', 'U', 'p', 'P'];
    if (blocked.includes(event.key)) event.preventDefault();
  }, { signal: pageSignal });

  // 5) Rasmni sudrab (drag) olishni bloklash
  document.addEventListener('dragstart', function (event) {
    if (event.target && event.target.tagName === 'IMG') event.preventDefault();
  }, { signal: pageSignal });
}

function bootSiteInteractions() {
  // Asosiy: turbo:load — Turbo rendering tugagach ishlaydi (birinchi yuklash va navigatsiya).
  // Bu sahifa to'liq tayyor bo'lgandan keyin listener'lar bog'lanishini kafolatlaydi.
  document.addEventListener('turbo:load', initSitePage);

  // Zaxira: Turbo ishlamasa (masalan, yuklanish xatosi) — DOMContentLoaded orqali.
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () {
      setTimeout(function () {
        if (!pageAbortController) {
          initSitePage();
        }
      }, 100);
    });
  } else {
    setTimeout(function () {
      if (!pageAbortController) {
        initSitePage();
      }
    }, 100);
  }
}

bootSiteInteractions();
