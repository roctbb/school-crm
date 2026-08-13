function shortYear(year) {
    return String(year % 100).padStart(2, "0");
}

export function getAcademicYear(referenceDate = new Date()) {
    const currentYear = referenceDate.getFullYear();
    const startsThisYear = referenceDate.getMonth() >= 8;
    const startYear = startsThisYear ? currentYear : currentYear - 1;

    return `${shortYear(startYear)}/${shortYear(startYear + 1)}`;
}

export function normalizeAcademicYear(value) {
    const match = String(value ?? "")
        .trim()
        .match(/^(\d{2}|\d{4})\s*[/.\-–—]\s*(\d{2}|\d{4})$/);

    if (!match) return null;

    const startYear = Number(match[1].slice(-2));
    const endYear = Number(match[2].slice(-2));
    return `${shortYear(startYear)}/${shortYear(endYear)}`;
}

export function currentAcademicYearGroup(groups = [], referenceDate = new Date()) {
    const currentAcademicYear = getAcademicYear(referenceDate);
    return groups.find(group => normalizeAcademicYear(group) === currentAcademicYear)
        ?? groups[groups.length - 1]
        ?? null;
}
