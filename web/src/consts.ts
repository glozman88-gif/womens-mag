export const SITE = {
  name: "Glyanec",
  tagline: "Журнал о моде, красоте и жизни",
  description:
    "Женский онлайн-журнал: тренды моды и красоты, звёзды шоу-бизнеса, отношения и психология, стиль жизни.",
  defaultAuthor: "Редакция Glyanec",
  twitterHandle: "@glyanec",
  locale: "ru_RU",
  lang: "ru",
} as const;

export const NAV: { label: string; href: string }[] = [
  { label: "Звёзды", href: "/zvezdy" },
  { label: "Красота", href: "/krasota" },
  { label: "Мода", href: "/moda" },
  { label: "Отношения", href: "/otnosheniya" },
  { label: "Психология", href: "/psihologiya" },
  { label: "Стиль жизни", href: "/stil-zhizni" },
];
