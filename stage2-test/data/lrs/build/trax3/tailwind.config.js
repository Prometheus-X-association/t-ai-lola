const defaultTheme = require("tailwindcss/defaultTheme");

/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php",
        "./storage/framework/views/*.php",
        "./trax/core/starter/resources/views/**/*.blade.php",
        "./trax/core/starter/resources/js/**/*.vue",
        "./trax/extended/resources/views/**/*.blade.php",
        "./trax/extended/resources/js/**/*.vue",
    ],

    theme: {
        extend: {
            fontFamily: {
                sans: ["Inter var", ...defaultTheme.fontFamily.sans],
            },
        },
    },

    plugins: [require("@tailwindcss/forms")],

    darkMode: "class",
};
