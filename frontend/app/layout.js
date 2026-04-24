import "./globals.css";

export const metadata = {
  title: "Porównywarka cen",
};

export default function RootLayout({ children }) {
  return (
    <html lang="pl">
      <head>
        <script
          dangerouslySetInnerHTML={{
            __html: `
              (function() {
                const saved = localStorage.getItem("theme");
                if (saved === "dark") {
                  document.documentElement.classList.add("dark");
                } else {
                  document.documentElement.classList.remove("dark");
                }
              })();
            `,
          }}
        />
      </head>

      <body className="bg-gray-100 dark:bg-gray-900 text-black dark:text-white">
        {children}
      </body>
    </html>
  );
}
