import useMainStore from "@/stores/mainStore.js";

let empty = function (obj) {
    return !obj || Object.keys(obj).length === 0
}

const hasTimePart = (d) => {
    return (d.getHours() !== 0 || d.getMinutes() !== 0);
}

const external_url = (path) => {
    return process.env.VUE_APP_MAINHOST + path
}

const formatDate = (d) => {
    return d.getDate() + "." + ('0' + (d.getMonth() + 1)).slice(-2) + "." + d.getFullYear()
}

const formatDateTime = (d) => {
    if (hasTimePart(d)) {
        return d.getDate() + "." + ('0' + (d.getMonth() + 1)).slice(-2) + "." + d.getFullYear() + " " + d.getHours() + ":" + ('0' + d.getMinutes()).slice(-2)
    } else {
        return d.getDate() + "." + ('0' + (d.getMonth() + 1)).slice(-2) + "." + d.getFullYear()
    }
}

const copy = function (obj) {
    return JSON.parse(JSON.stringify(obj))
}

const isString = function (value) {
    return typeof value === 'string' || value instanceof String;
}

const searchForArray = function (haystack, needle) {
    var i, j, current;
    for (i = 0; i < haystack.length; ++i) {
        if (needle.length === haystack[i].length) {
            current = haystack[i];
            for (j = 0; j < needle.length && needle[j] === current[j]; ++j) ;
            if (j === needle.length)
                return true;
        }
    }
    return false;
}

function toBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.readAsDataURL(file);
        reader.onloadend = () => resolve(reader.result.split(';base64,')[1]);
        reader.onerror = error => reject(error);
    })
}

function fillPatientData(text, patient) {
    if (isString(text)) {
        text = text.replace('<PATIENT_NAME>', patient.name)
    }
    return text
}

function capitalize(str) {
    if (!str) return ''; // Если строка пустая или не передана, вернуть пустую строку
    return str.charAt(0).toUpperCase() + str.slice(1);
}

function getAcademicYear() {
    const now = new Date();
    const currentYear = now.getFullYear();
    const currentMonth = now.getMonth() + 1; // Месяцы в JS считаются с 0, поэтому прибавляем 1

    let startYear, endYear;

    if (currentMonth >= 9) {
        // С сентября по декабрь включительно используем текущий год и следующий
        startYear = currentYear % 100;
        endYear = (currentYear + 1) % 100;
    } else {
        // С января по август используем предыдущий год и текущий
        startYear = (currentYear - 1) % 100;
        endYear = currentYear % 100;
    }

    // Преобразуем в формат "24/25" с ведущим нулём при необходимости
    return `${String(startYear).padStart(2, '0')}/${String(endYear).padStart(2, '0')}`;
}

const formatValue = function (value) {
    // Если value — это массив, соединяем элементы через запятую
    if (Array.isArray(value)) {
        return value.join(", ");
    }
    // Иначе возвращаем как есть
    return value;
}

function parseDate(dateString) {
    // dateString вроде "01.10.2023"
    try {
        const [day, month, year] = dateString.split('.');
        return new Date(+year, +month - 1, +day);
    }
    catch (e) {
        return undefined
    }
}

const isEventActive = function (event, object) {
    const start = event.attributes.start;
    const end = event.attributes.end;
    const children = event.children;

    // Проверяем, что в children есть объект с нужным id
    const hasObject = Array.isArray(children) && children.some(child => child.id === object.id);
    if (!hasObject) {
        return false;
    }

    // Преобразуем строки в Date
    const startDate = start ? parseDate(start) : null;
    const endDate = end ? parseDate(end) : null;
    const now = new Date();

    if (endDate) {
        endDate.setHours(23, 59, 59, 999);
    }

    // Функция для сравнения только года, месяца и дня
    const isSameDay = (d1, d2) =>
        d1.getFullYear() === d2.getFullYear() &&
        d1.getMonth() === d2.getMonth() &&
        d1.getDate() === d2.getDate();

    // 1) Если start и end заданы — проверяем, что now попадает в период [startDate, endDate]
    if (startDate && endDate) {
        return now >= startDate && now <= endDate;
    }

    // 2) Если только start, то событие активно, если сегодняшняя дата совпадает со start
    if (startDate && !endDate) {
        return isSameDay(now, startDate);
    }

    // Если нет startDate, возвращаем false
    return false;
}

const hasAccessToObject = function(object) {
    let profile = useMainStore().profile;
    if (!profile) return false;

    if (profile.role === 'admin' || profile.role === 'teacher') {
        return true;
    }

    for (let owner of object.owners) {
        if (owner.id === profile.id) {
            return true;
        }
    }

    return false;
}

const hasAdminAccess = function() {
    let profile = useMainStore().profile;
    if (!profile) return false;

    return profile.role === 'admin';
}

const hasTeacherAccess = function() {
    let profile = useMainStore().profile;
    if (!profile) return false;

    return profile.role === 'admin' || profile.role === 'teacher';
}


export {
    searchForArray,
    empty,
    external_url,
    capitalize,
    formatDate,
    formatDateTime,
    copy,
    toBase64, isString, fillPatientData, getAcademicYear, formatValue, isEventActive, parseDate, hasAccessToObject, hasAdminAccess, hasTeacherAccess
}