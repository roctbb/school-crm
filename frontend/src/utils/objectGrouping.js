export const MONTH_GROUPING_PREFIX = "month:";
export const EMPTY_GROUP_LABEL = "Без группы";

const MONTH_NAMES = [
    "Январь", "Февраль", "Март", "Апрель", "Май", "Июнь",
    "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь",
];

export function monthGroupingCode(attributeCode) {
    return `${MONTH_GROUPING_PREFIX}${attributeCode}`;
}

function monthGroupingName(attributeName) {
    const dateName = attributeName?.match(/^Дата\s+(.+)$/i);
    return dateName ? `Месяц ${dateName[1]}` : `${attributeName}: по месяцам`;
}

export function buildGroupingOptions(attributes = []) {
    return (attributes || []).flatMap(attribute => {
        const options = [];
        if (attribute.group) {
            options.push({...attribute, sourceCode: attribute.code, groupingMode: "value"});
        }
        if (attribute.type === "date") {
            options.push({
                ...attribute,
                code: monthGroupingCode(attribute.code),
                name: monthGroupingName(attribute.name),
                sourceCode: attribute.code,
                groupingMode: "month",
            });
        }
        return options;
    });
}

function dateMonthKey(value) {
    if (typeof value !== "string") return null;

    let year;
    let month;
    const crmDate = value.match(/^(\d{2})\.(\d{2})\.(\d{4})$/);
    const isoDate = value.match(/^(\d{4})-(\d{2})-\d{2}/);
    if (crmDate) {
        [, , month, year] = crmDate;
    } else if (isoDate) {
        [, year, month] = isoDate;
    } else {
        return null;
    }

    const monthNumber = Number(month);
    if (monthNumber < 1 || monthNumber > 12) return null;
    return `${year}-${String(monthNumber).padStart(2, "0")}`;
}

export function groupingKey(value, groupingOption) {
    if (value === null || value === undefined || value === "") return EMPTY_GROUP_LABEL;
    if (groupingOption?.groupingMode === "month") {
        return dateMonthKey(value) || EMPTY_GROUP_LABEL;
    }
    return String(value);
}

export function groupingLabel(groupKey, groupingOption) {
    if (groupingOption?.groupingMode !== "month" || groupKey === EMPTY_GROUP_LABEL) return groupKey;
    const match = groupKey.match(/^(\d{4})-(\d{2})$/);
    if (!match) return groupKey;
    const monthName = MONTH_NAMES[Number(match[2]) - 1];
    return monthName ? `${monthName} ${match[1]}` : groupKey;
}
