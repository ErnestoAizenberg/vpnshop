// Constants
const BASE_URL = 'https://vite.pythonanywhere.com'
const API_ENDPOINT = 'https://vite.pythonanywhere.com/api'

// State management
const appState = {
  user: {
    userId: window.location.pathname.split('/').pop(),
    username: '',
    status: '',
    vpnConfig: '',
    expiresAt: '',
    daysLeft: 0,
    trafficUsed: '0 GiB',
    trafficLimit: '0 GiB',
    trafficPercent: '0%'
  },
  platforms: {
    android: {
      id: "android",
      name: "Android",
      icon: "device-mobile",
      providers: {
        happ: {
          name: "Happ",
          icon: "star",
          sources: [
            {
              name: "Открыть в Google Play",
              url: "https://play.google.com/store/apps/details?id=com.happproxy",
            },
            {
              name: "Скачать APK",
              url: "https://github.com/Happ-proxy/happ-android/releases/latest/download/Happ.apk"
            },
          ],
          instructions: [
            {
              title: "Установите и откройте Happ",
              description: "Откройте страницу в Google Play и установите приложение. Или установите приложение из APK файла напрямую, если Google Play не работает.",
              icon: "download"
            },
            {
              title: "Добавить подписку",
              description: "Нажмите кнопку ниже, чтобы добавить подписку",
              icon: "cloud-download"
            },
            {
              title: "Подключите и используйте",
              description: "Откройте приложение и подключитесь к серверу",
              icon: "check"
            },
          ],
        },
        v2raytun: {
          name: "v2RayTun",
          icon: "",
          sources: [
            {
              name: "Открыть в Google Play",
              url: "https://play.google.com/store/apps/details?id=com.v2raytun.android&hl=ru",
            }
          ],
          instructions: [
            {
              title: "Установите и откройте v2RayTun",
              description: "Откройте страницу в Google Play и установите приложение.",
              icon: "download"
            },
            {
              title: "Добавить подписку",
              description: "Нажмите кнопку ниже, чтобы импортировать конфигурацию",
              icon: "cloud-download"
            },
            {
              title: "Подключите и используйте",
              description: "Откройте приложение и подключитесь к серверу",
              icon: "check"
            },
          ],
        },
      },
    },
    ios: {
      id: "ios",
      name: "iOS",
      icon: "device-mobile",
      providers: {
        happ: {
          name: "Happ",
          icon: "star",
          sources: [
            {
              name: "Открыть в App Store(Rus)",
              url: "https://apps.apple.com/ru/app/happ-proxy-utility-plus/id6746188973",
            },
            {
              name: "Открыть в App Store(Global)",
              url: "https://apps.apple.com/us/app/happ-proxy-utility/id6504287215"
            },
          ],
          instructions: [
            {
              title: "Установите и откройте Happ",
              description: "Откройте страницу в App Store и установите приложение(Если приложение недостпуно попробуйте другую ссылку Rus или Global). Запустите его, в окне разрешения VPN-конфигурации нажмите Allow и введите свой пароль.",
              icon: "download"
            },
            {
              title: "Добавить подписку",
              description: "Нажмите кнопку ниже — приложение откроется, и подписка добавится автоматически.",
              icon: "cloud-download"
            },
            {
              title: "Подключите и используйте",
              description: "В главном разделе нажмите большую кнопку включения в центре для подключения к VPN. Не забудьте выбрать сервер в списке серверов. При необходимости выберите другой сервер из списка серверов.",
              icon: "check"
            },
          ],
        },
        v2raytun: {
          name: "v2RayTun",
          icon: "",
          sources: [
            {
              name: "Открыть в App Store",
              url: "https://apps.apple.com/ru/app/v2raytun/id6476628951",
            }
          ],
          instructions: [
            {
              title: "Установите и откройте v2RayTun",
              description: "Откройте страницу в App Store и установите приложение. Запустите его, в окне разрешения VPN-конфигурации нажмите Allow и введите свой пароль.",
              icon: "download"
            },
            {
              title: "Добавить подписку",
              description: "Нажмите кнопку ниже — приложение откроется, и подписка добавится автоматически.",
              icon: "cloud-download"
            },
            {
              title: "Подключите и используйте",
              description: "Откройте приложение и подключитесь к серверу",
              icon: "check"
            },
          ],
        },
      },
    },
    pc: {
      id: "pc",
      name: "ПК",
      icon: "device-desktop",
      providers: {
        hiddify: {
          name: "Hiddify",
          icon: "star",
          sources: [
            {
              name: "Windows",
              url: "https://github.com/hiddify/hiddify-app/releases/download/v2.5.7/Hiddify-Windows-Setup-x64.exe"
            },
            {
              name: "macOS",
              url: "https://github.com/hiddify/hiddify-app/releases/download/v2.5.7/Hiddify-MacOS.dmg"
            },
            {
              name: "Linux",
              url: "https://github.com/hiddify/hiddify-app/releases/download/v2.5.7/Hiddify-Linux-x64.AppImage"
            }
          ],
          instructions: [
            {
              title: "Скачайте Hiddify",
              description: "В главном разделе нажмите большую кнопку включения в центре для подключения к VPN. При необходимости выберите другой сервер в разделе Прокси.",
              icon: "download"
            },
            {
              title: "Выбор/смена сервера",
              description: "После подключения, слева выберите 'Прокси' и выберите нужный сервер.",
              icon: "info-circle"
            },
            {
              title: "Добавить подписку",
              description: "Нажмите кнопку ниже, чтобы добавить подписку",
              icon: "cloud-download"
            },
            {
              title: "Подключите и используйте",
              description: "В главном разделе нажмите большую кнопку включения в центре для подключения к VPN. Не забудьте выбрать сервер в списке серверов. При необходимости выберите другой сервер из списка серверов.",
              icon: "check"
            }
          ]
        },
        clash: {
          name: "Clash Verge",
          icon: "bolt",
          sources: [
            {
              name: "Windows",
              url: "https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.2.2/Clash.Verge_2.2.2_x64-setup.exe"
            },
            {
              name: "macOS (Intel)",
              url: "https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.2.2/Clash.Verge_2.2.2_x64.dmg"
            },
            {
              name: "macOS (Apple Silicon)",
              url: "https://github.com/clash-verge-rev/clash-verge-rev/releases/download/v2.2.2/Clash.Verge_2.2.2_aarch64.dmg"
            },
            {
              name: "Linux",
              url: "https://github.com/clash-verge-rev/clash-verge-rev/releases"
            },
          ],
          instructions: [
            {
              title: "Скачайте Clash Verge",
              description: "Выберите подходящую версию для вашего устройства, нажмите на кнопку ниже и установите приложение.",
              icon: "download"
            },
            {
              title: "Смена языка",
              description: "При установке приложения выбираем English, после запуска приложения язык будет Русский.",
              icon: "info-circle"
            },
            {
              title: "Добавить подписку",
              description: "Нажмите кнопку ниже, чтобы добавить подписку",
              icon: "cloud-download"
            },
            {
              title: "Подключите и используйте",
              description: "Выбрать сервер можно в разделе Прокси, включить VPN можно в разделе Настройки. Установите переключатель TUN Mode в положение ВКЛ.",
              icon: "check"
            }
          ],
        }
      },
    },
  },
  currentPlatform: "pc",
  currentProvider: "hiddify"
};

// SVG Icons
const icons = {
  "star": `<path d="M12 17.75l-6.172 3.245l1.179 -6.873l-5 -4.867l6.9 -1l3.086 -6.253l3.086 6.253l6.9 1l-5 4.867l1.179 6.873z"></path>`,
  "bolt": `<path d="M13 3l0 7l6 0l-8 11l0 -7l-6 0l8 -11z"></path>`,
  "download": `<path d="M4 17v2a2 2 0 0 0 2 2h12a2 2 0 0 0 2 -2v-2"></path><path d="M7 11l5 5l5 -5"></path><path d="M12 4l0 12"></path>`,
  "info-circle": `<path d="M3 12a9 9 0 1 0 18 0a9 9 0 0 0 -18 0"></path><path d="M12 9h.01"></path><path d="M11 12h1v4h1"></path>`,
  "cloud-download": `<path d="M19 18a3.5 3.5 0 0 0 0 -7h-1a5 4.5 0 0 0 -11 -2a4.6 4.4 0 0 0 -2.1 8.4"></path><path d="M12 13l0 9"></path><path d="M9 19l3 3l3 -3"></path>`,
  "check": `<path d="M5 12l5 5l10 -10"></path>`,
  "device-desktop": `<path d="M3 5a1 1 0 0 1 1 -1h16a1 1 0 0 1 1 1v10a1 1 0 0 1 -1 1h-16a1 1 0 0 1 -1 -1v-10z"></path><path d="M7 20h10"></path><path d="M9 16v4"></path><path d="M15 16v4"></path>`,
  "device-mobile": `<path d="M6 5a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v14a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2v-14z"></path><path d="M11 4h2"></path><path d="M12 17v.01"></path>`,
  "external-link": `<path d="M12 6h-6a2 2 0 0 0 -2 2v10a2 2 0 0 0 2 2h10a2 2 0 0 0 2 -2v-6"></path><path d="M11 13l9 -9"></path><path d="M15 4h5v5"></path>`,
  "user": `<path d="M8 7a4 4 0 1 0 8 0a4 4 0 0 0 -8 0"></path><path d="M6 21v-2a4 4 0 0 1 4 -4h4a4 4 0 0 1 4 4v2"></path>`,
  "calendar": `<path d="M4 7a2 2 0 0 1 2 -2h12a2 2 0 0 1 2 2v12a2 2 0 0 1 -2 2h-12a2 2 0 0 1 -2 -2v-12z"></path><path d="M16 3v4"></path><path d="M8 3v4"></path><path d="M4 11h16"></path><path d="M11 15h1"></path><path d="M12 15v3"></path>`,
  "arrows-up-down": `<path d="M7 3l0 18"></path><path d="M10 6l-3 -3l-3 3"></path><path d="M20 18l-3 3l-3 -3"></path><path d="M17 21l0 -18"></path>`,
  "chevron-down": `<path d="M6 9l6 6l6 -6"></path>`
};

/**
 * Fetches user subscription data from the API
 * @param {number} userId - The user ID to fetch data for
 * @returns {Promise<Object>} - The user subscription data
 */
async function fetchUserData(userId) {
  try {
    const url = `${API_ENDPOINT}/subscription/${userId}`
    const response = await fetch(url);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching user data:', error);
    throw error;
  }
}

/**
 * Formats user data for display
 * @param {Object} data - Raw user data from API
 * @returns {Object} - Formatted user data
 */
function formatUserData(data) {
  return {
    userId: appState.user.userId,
    username: data.username || 'N/A',
    status: data.status || 'Неизвестно',
    expiresAt: data.expiresAt || 'N/A',
    daysLeft: data.daysLeft || 0,
    trafficUsed: `${data.trafficUsed || 0} GiB`,
    trafficLimit: `${data.trafficLimit || 0} GiB`,
    trafficPercent: `${data.trafficPercent || 0}%`
  };
}

/**
 * Generates an SVG icon
 * @param {string} iconName - Name of the icon to generate
 * @param {number} size - Size of the icon in pixels
 * @param {number} stroke - Stroke width of the icon
 * @param {string} color - Color of the icon
 * @returns {string} - SVG markup for the icon
 */
function getIcon(iconName, size = 16, stroke = 2, color = "currentColor") {
  if (!icons[iconName]) {
    console.warn(`Icon "${iconName}" not found`);
    return '';
  }
  return `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="${color}" stroke-width="${stroke}" stroke-linecap="round" stroke-linejoin="round">${icons[iconName]}</svg>`;
}

/**
 * Renders the application UI
 */
function renderApp() {
  const currentPlatform = appState.platforms[appState.currentPlatform];
  const currentProvider = currentPlatform.providers[appState.currentProvider];

  document.getElementById('app').innerHTML = `
    <div class="header">
      <h1 class="title">Подписка</h1>
      <button class="btn btn-outline" id="get-link-btn">Получить ссылку</button>
    </div>

    <div class="card">
      <div class="accordion active" id="subscription-info">
        <div class="accordion-header" onclick="toggleAccordion('subscription-info')">
          <div class="accordion-title">
            <div class="flex items-center">
              <span>${appState.user.username}</span>
              <span class="text-muted text-small mt-1">Истекает через ${appState.user.daysLeft} дня</span>
            </div>
          </div>
          <div class="flex items-center">
            <div class="stat-icon" style="color: var(--tg-green-color); margin-right: 12px;">
              ${getIcon('check', 20)}
            </div>
            ${getIcon('chevron-down', 16)}
          </div>
        </div>
        <div class="accordion-content" style="max-height: 500px;">
          <div class="stats-grid">
            <div class="stat-item">
              <div class="stat-label">
                ${getIcon('user', 16)}
                Имя пользователя
              </div>
              <div class="stat-value">${appState.user.username}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">
                ${getIcon('check', 16)}
                Статус
              </div>
              <div class="stat-value">${appState.user.status}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">
                ${getIcon('calendar', 16)}
                Истекает
              </div>
              <div class="stat-value">${appState.user.expiresAt}</div>
            </div>
            <div class="stat-item">
              <div class="stat-label">
                ${getIcon('arrows-up-down', 16)}
                Трафик
              </div>
              <div class="stat-value">${appState.user.trafficUsed} / ${appState.user.trafficLimit}</div>
              <div class="progress-container mt-1">
                <div class="progress-bar" style="width: ${appState.user.trafficPercent}%"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <div class="card">
      <div class="flex items-center justify-between mb-2">
        <h2 class="title">Установка</h2>
        <div class="select" id="device-select">
          <div class="select-toggle" onclick="toggleSelect('device-select')">
            <div class="flex items-center">
              ${getIcon(currentPlatform.icon, 20, 2, "currentColor")}
              <span>${currentPlatform.name}</span>
            </div>
            ${getIcon('chevron-down', 16)}
          </div>
          <div class="select-dropdown">
            ${Object.values(appState.platforms).map(platform => `
              <div class="select-option" onclick="selectOption('device-select', '${platform.id}', '${platform.name}')">
                <span>${platform.name}</span>
              </div>
            `).join('')}
          </div>
        </div>
      </div>

      <div class="btn-group">
        ${Object.entries(currentPlatform.providers).map(([id, provider]) => `
          <button class="btn ${appState.currentProvider === id ? 'btn-light' : 'btn-outline'}"
                  onclick="changeProvider('${id}')"
                  style="flex: 1;">
            ${provider.icon ? getIcon(provider.icon, 16, 2, appState.currentProvider === id ? "gold" : "currentColor") : ''}
            ${provider.name}
          </button>
        `).join('')}
      </div>

      <div class="timeline">
        ${currentProvider.instructions.map((step, index) => `
          <div class="timeline-item" ${index === 0 ? 'data-active="true"' : ''}>
            <div class="timeline-bullet">
              ${getIcon(step.icon, 14, 2, "white")}
            </div>
            <div class="timeline-content">
              <h3 class="timeline-title">${step.title}</h3>
              <p class="timeline-description">
                ${step.description}
              </p>
              ${index === 0 ? `
                <div class="btn-group">
                  ${currentProvider.sources.map((source) => `
                    <a href="${source.url}" target="_blank" class="btn btn-light">
                      ${getIcon('external-link', 14)}
                      ${source.name}
                    </a>
                  `).join('')}
                </div>
              ` : ''}
              ${index === 2 ? `
                <button class="btn btn-primary mt-2" id="add-subscription-btn">
                  Добавить подписку
                </button>
              ` : ''}
            </div>
          </div>
        `).join('')}
      </div>
    </div>

    <div style="text-align: center; margin-top: var(--tg-spacing);">
      <button class="btn btn-outline">
        <div class="flex items-center">
          <span>Русский</span>
          ${getIcon('chevron-down', 16, 1.5)}
        </div>
      </button>
    </div>
  `;

  // Initialize event listeners
  document.getElementById('get-link-btn')?.addEventListener('click', getLink);
  document.getElementById('add-subscription-btn')?.addEventListener('click', () => addSubscription(appState.user.userId));
}

/**
 * Toggles an accordion element
 * @param {string} id - The ID of the accordion element
 */
function toggleAccordion(id) {
  const accordion = document.getElementById(id);
  if (!accordion) return;

  const content = accordion.querySelector('.accordion-content');
  if (!content) return;

  if (accordion.classList.contains('active')) {
    content.style.maxHeight = null;
    accordion.classList.remove('active');
  } else {
    content.style.maxHeight = content.scrollHeight + "px";
    accordion.classList.add('active');
  }
}

/**
 * Toggles a select dropdown
 * @param {string} id - The ID of the select element
 */
function toggleSelect(id) {
  const select = document.getElementById(id);
  if (select) {
    select.classList.toggle('active');
  }
}

/**
 * Selects an option from a dropdown
 * @param {string} selectId - The ID of the select element
 * @param {string} platformId - The ID of the platform to select
 * @param {string} platformName - The name of the platform (unused)
 */
function selectOption(selectId, platformId, platformName) {
  if (!appState.platforms[platformId]) {
    console.error(`Platform ${platformId} not found`);
    return;
  }

  appState.currentPlatform = platformId;
  // Reset provider to first available when platform changes
  const firstProvider = Object.keys(appState.platforms[platformId].providers)[0];
  appState.currentProvider = firstProvider;
  renderApp();
}

/**
 * Changes the current provider
 * @param {string} providerId - The ID of the provider to switch to
 */
function changeProvider(providerId) {
  const currentPlatform = appState.platforms[appState.currentPlatform];
  if (!currentPlatform.providers[providerId]) {
    console.error(`Provider ${providerId} not found for platform ${appState.currentPlatform}`);
    return;
  }

  appState.currentProvider = providerId;
  renderApp();
}

/**
 * Copies the subscription link to clipboard
 */
function getLink(userId) {
  try {
    userConfigLink = `${BASE_URL}/${userId}`;
    navigator.clipboard.writeText(userConfigLink).then(() => {
      alert('Ссылка скопирована в буфер обмена');
    }).catch(err => {
      console.error('Could not copy text: ', err);
      alert('Не удалось скопировать ссылку');
    });
  } catch (error) {
    console.error('Clipboard API not available', error);
    // Fallback for browsers that don't support Clipboard API
    const textarea = document.createElement('textarea');
    textarea.value = userConfigLink;
    document.body.appendChild(textarea);
    textarea.select();
    try {
      document.execCommand('copy');
      alert('Ссылка скопирована в буфер обмена');
    } catch (err) {
      console.error('Fallback copy failed', err);
      alert('Не удалось скопировать ссылку');
    }
    document.body.removeChild(textarea);
  }
}

/**
 * Opens the appropriate deep link for adding a subscription
 */
function addSubscription(userId) {
  if (!userId) {
    console.error('User ID is not defined');
    alert('Не удалось определить ID пользователя');
    return;
  }

  const userConfigLink = `${encodeURIComponent(BASE_URL)}/${userId}`;
  console.log(`userConfigLink: ${userConfigLink}`);

  const deepLinks = {
    clash: `clash://install-config?url=${userConfigLink}`,
    happ: `happ://add/${userConfigLink}`,
    v2raytun: `v2raytun://import?url=${userConfigLink}`
  };

  const appLink = deepLinks[appState.currentProvider] || `${BASE_URL}/${userId}`;
  window.open(appLink, '_blank');
}

/**
 * Initializes the application
 */
async function initApp() {
  try {
    // Load user data
    const userData = await fetchUserData(appState.user.userId);
    appState.user = formatUserData(userData);

    // Render the app
    renderApp();

    // Close dropdowns when clicking outside
    document.addEventListener('click', function(event) {
      if (!event.target.closest('.select')) {
        document.querySelectorAll('.select').forEach(select => {
          select.classList.remove('active');
        });
      }
    });
  } catch (error) {
    console.error('Failed to initialize app:', error);
    // Show error state to user
    document.getElementById('app').innerHTML = `
      <div class="error-state">
        <h2>Ошибка загрузки</h2>
        <p>Не удалось загрузить данные. Пожалуйста, попробуйте позже.</p>
        <button class="btn btn-primary" onclick="initApp()">Попробовать снова</button>
      </div>
    `;
  }
}

// Start the application when DOM is loaded
document.addEventListener('DOMContentLoaded', initApp);
