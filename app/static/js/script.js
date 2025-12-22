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






document.getElementById("enableTranslation").addEventListener("change", function() {
document.getElementById("dest_lang").disabled = !this.checked;
});

document.getElementById("generateBtn").addEventListener("click", function(event) {
event.preventDefault(); // جلوگیری از ارسال فرم به صورت پیش‌فرض

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
    } else {
        showErrorModal("خطایی رخ داده. لطفا چک کنید ویدیو به درستی اپلود شده باشه!");
    }
})
.catch(error => {
    statusMessage.remove();
    showErrorModal("خطایی رخ داده. لطفا چک کنید ویدیو به درستی اپلود شده باشه!");
    console.error("Error:", error);
});
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

    // تنظیم پیام خطا
    errorMessage.textContent = message;

    // نمایش مدال
    modal.style.display = "flex";

    // افزودن رویداد برای بستن مدال
    const closeButton = modal.querySelector(".close-btn");
    closeButton.onclick = () => {
        modal.style.display = "none";
    };

    // بستن مدال با کلیک بیرون از آن
    window.onclick = (event) => {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    };
}









