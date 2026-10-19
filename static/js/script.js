let cachedLogoBase64 = null;
let renderTimeout = null;

function toggleDarkMode() {
    const html = document.documentElement;
    html.setAttribute('data-bs-theme',
        html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark');
}

function getQRTextData() {
    return document.getElementById('text_data')?.value || 'https://domainanda.com';
}

function debouncedRender() {
    clearTimeout(renderTimeout);
    renderTimeout = setTimeout(renderRealtimeQR, 150);
}

function handleLogoChange() {
    const logoInput = document.getElementById('logo');
    const file = logoInput?.files?.[0];
    if (!file) {
        cachedLogoBase64 = null;
        debouncedRender();
        return;
    }

    const reader = new FileReader();
    reader.onload = event => {
        cachedLogoBase64 = event.target.result;
        debouncedRender();
    };
    reader.readAsDataURL(file);
}

function renderRealtimeQR() {
    const container = document.getElementById('canvasPreview');
    if (!container || typeof QRCode === 'undefined') return;

    const darkColor = document.getElementById('dark_color')?.value || '#000000';
    const lightColor = document.getElementById('light_color')?.value || '#ffffff';
    const darkVal = document.getElementById('dark_color_val');
    const lightVal = document.getElementById('light_color_val');
    if (darkVal) darkVal.textContent = darkColor.toUpperCase();
    if (lightVal) lightVal.textContent = lightColor.toUpperCase();

    container.innerHTML = '';
    const config = {
        text: getQRTextData(),
        width: 200,
        height: 200,
        colorDark: darkColor,
        colorLight: lightColor,
        correctLevel: QRCode.CorrectLevel.H
    };
    if (cachedLogoBase64) {
        config.logo = cachedLogoBase64;
        config.logoWidth = 75;
        config.logoHeight = 75;
        config.logoBackgroundTransparent = true;
    }
    new QRCode(container, config);
}

document.addEventListener('DOMContentLoaded', () => {
    const logoInput = document.getElementById('logo');
    if (logoInput) logoInput.addEventListener('change', handleLogoChange);

    document.querySelectorAll('#text_data, #dark_color, #light_color')
        .forEach(input => input.addEventListener('input', debouncedRender));
    renderRealtimeQR();
});
