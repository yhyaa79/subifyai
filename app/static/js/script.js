const bottomSheet = document.querySelector('.bottom-sheet');
const dragHandle = document.querySelector('.drag-handle');
const sheetContent = document.querySelector('.sheet-content');

// Create a toggle icon
const toggleIcon = document.createElement('div');
toggleIcon.innerHTML = '<i class="fas fa-angle-up"></i>'; // Up arrow when closed
toggleIcon.style.top = '10px';
toggleIcon.style.left = '50%';
toggleIcon.style.textAlign = 'center';
toggleIcon.style.fontSize = '25px';
toggleIcon.style.cursor = 'pointer';
toggleIcon.style.zIndex = '1001';




// تولید یا دریافت شناسه منحصر به فرد کاربر از localStorage
function getOrCreateUserId() {
    let userId = localStorage.getItem('subify_user_id');
    if (!userId) {
        // تولید یک شناسه تصادفی ساده (کافی برای این منظور)
        userId = 'user_' + Math.random().toString(36).substr(2, 9) + '_' + Date.now();
        localStorage.setItem('subify_user_id', userId);
    }
    return userId;
}

// وقتی صفحه لود شد، فیلد مخفی user_id را پر کن
window.addEventListener('DOMContentLoaded', () => {
    const userId = getOrCreateUserId();
    
    // ایجاد یا به‌روزرسانی فیلد مخفی در فرم
    let userIdInput = document.getElementById('user_id');
    if (!userIdInput) {
        userIdInput = document.createElement('input');
        userIdInput.type = 'hidden';
        userIdInput.name = 'user_id';
        userIdInput.id = 'user_id';
        document.querySelector('form').appendChild(userIdInput);
    }
    userIdInput.value = userId;
});


// Remove the existing drag handle
dragHandle.remove();

// Add the toggle icon to the bottom sheet
bottomSheet.insertBefore(toggleIcon, sheetContent);

// Initial state
let isOpen = false;
bottomSheet.style.height = '100px';
sheetContent.style.display = 'none';

// Toggle function
function toggleBottomSheet() {
    const maxHeight = window.innerHeight * 0.88; // Maximum height
    const minHeight = 100; // Minimum height

    if (!isOpen) {
        // Open the bottom sheet
        bottomSheet.style.height = `${maxHeight}px`;
        sheetContent.style.display = 'block';
        sheetContent.style.overflow = 'auto';
        toggleIcon.innerHTML = '<i class="fas fa-angle-down"></i>'; // Down arrow when open
        isOpen = true;
    } else {
        // Close the bottom sheet
        bottomSheet.style.height = `${minHeight}px`;
        sheetContent.style.display = 'none';
        toggleIcon.innerHTML = '<i class="fas fa-angle-up"></i>'; // Up arrow when closed
        isOpen = false;
    }
}

// Add click event listener to the toggle icon
toggleIcon.addEventListener('click', toggleBottomSheet);

// Remove existing touch event listeners
bottomSheet.removeEventListener('touchstart', () => {});
bottomSheet.removeEventListener('touchmove', () => {});
bottomSheet.removeEventListener('touchend', () => {});






document.getElementById("enableTranslation").addEventListener("change", function () {
    document.getElementById("dest_lang").disabled = !this.checked;
});

// نمایش نام فایل بعد از انتخاب
const fileInput = document.getElementById("fileUpload");
const uploadBox = document.querySelector(".upload-box");

// ایجاد المان برای نمایش نام فایل
const fileNameDisplay = document.createElement("p");
fileNameDisplay.classList.add("file-name");
fileNameDisplay.textContent = "فایلی انتخاب نشده";
fileNameDisplay.style.marginTop = "10px";
fileNameDisplay.style.fontSize = "14px";
fileNameDisplay.style.color = "#666";
uploadBox.appendChild(fileNameDisplay);

fileInput.addEventListener("change", function () {
    if (this.files && this.files.length > 0) {
        fileNameDisplay.textContent = this.files[0].name;
        fileNameDisplay.style.color = "#2c8a2c";
    } else {
        fileNameDisplay.textContent = "فایلی انتخاب نشده";
        fileNameDisplay.style.color = "#666";
    }
});

// مدیریت کلیک دکمه شروع
document.getElementById("generateBtn").addEventListener("click", function (event) {
    event.preventDefault();

    // پاک کردن پیام‌های قبلی
    const existingStatus = document.querySelector(".status");
    if (existingStatus) existingStatus.remove();

    const existingDownloadButton = document.querySelector(".download-button");
    if (existingDownloadButton) existingDownloadButton.remove();

    // دکمه در حال پردازش
    const generateBtn = document.getElementById("generateBtn");
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> لطفا صبر کنید...';

    const formData = new FormData(document.querySelector("form"));

    fetch("/", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // موفقیت: نمایش دکمه دانلود
            const downloadButton = document.createElement("a");
            downloadButton.href = data.download_url;
            downloadButton.textContent = "دانلود زیرنویس";
            downloadButton.classList.add("download-button");
            downloadButton.setAttribute("download", "adjusted_subtitle.srt");
            document.querySelector(".download-section").appendChild(downloadButton);
        } else {
            // خطا: حالا پیام دقیق سرور رو نمایش بده
            let errorMessage = data.message || "خطایی ناشناخته رخ داد.";

            // اگر پیام شامل HTML بود (مثل پیام rate limit)، مستقیم استفاده کن
            showErrorModal(errorMessage);
        }
    })
    .catch(error => {
        console.error("Error:", error);
        showErrorModal("خطایی در ارتباط با سرور رخ داده است. لطفاً دوباره تلاش کنید.");
    })
    .finally(() => {
        generateBtn.disabled = false;
        generateBtn.innerHTML = '<i class="fas fa-play"></i> شروع';
    });
});

// حذف دکمه دانلود قدیمی در صورت وجود
const existingDownloadButton = document.querySelector(".download-button");
if (existingDownloadButton) {
    existingDownloadButton.remove();
}

// نمایش پیام لطفا صبر کنید
const statusMessage = document.createElement("label");
statusMessage.innerHTML = '<i class="fas fa-spinner fa-spin"></i> لطفا صبر کنید...';
statusMessage.classList.add("status");
document.querySelector(".download-section").appendChild(statusMessage);

// اطلاعات فرم را به فرم‌داده تبدیل کنید
const formData = new FormData(document.querySelector("form"));

// ارسال درخواست AJAX
fetch("/", {
        method: "POST",
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        // حذف پیام لطفا صبر کنید
        statusMessage.remove();

        if (data.success) {
            // اضافه کردن دکمه دانلود
            const downloadButton = document.createElement("a");
            downloadButton.href = data.download_url;
            downloadButton.textContent = "دانلود زیرنویس";
            downloadButton.classList.add("download-button");
            downloadButton.setAttribute("download", "adjusted_subtitle.srt");

            // اضافه کردن دکمه به بخش دانلود
            document.querySelector(".download-section").appendChild(downloadButton);
        } 
    })
    .catch(error => {
        statusMessage.remove();
        console.error("Error:", error);
    });



function showContent(index) {
    // انتخاب تمام تب‌ها و محتواها
    const tabs = document.querySelectorAll(".tab");
    const contents = document.querySelectorAll(".content");

    // حذف کلاس active از همه تب‌ها و محتواها
    tabs.forEach((tab) => tab.classList.remove("active"));
    contents.forEach((content) => content.classList.remove("active"));

    // اضافه کردن کلاس active به تب و محتوای انتخاب شده
    tabs[index].classList.add("active");
    contents[index].classList.add("active");
}


// نمایش مدال با پیام خطا
function showErrorModal(message) {
    const modal = document.getElementById("errorModal");
    const errorMessage = document.getElementById("errorMessage");

    // استفاده از innerHTML به جای textContent برای نمایش HTML
    errorMessage.innerHTML = message;

    modal.style.display = "flex";

    const closeButton = modal.querySelector(".close-btn");
    closeButton.onclick = () => {
        modal.style.display = "none";
    };

    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
}