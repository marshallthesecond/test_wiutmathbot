from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
import os

EXAMS_PATH = "samples"

main_keyboard = ReplyKeyboardMarkup(
    keyboard = [
        [KeyboardButton("WIUT Math Exam Samples")], [KeyboardButton("Help")],
    ],
    resize_keyboard=True,
)

# gets years in the exams folder
def get_folder():
    return sorted(
        [
            f for f in os.listdir(EXAMS_PATH)
            if os.path.isdir(os.path.join(EXAMS_PATH, f)) and not f.startswith('.')
        ]
    )

# get list of exam files in a selected year
def get_exam_files(year):
    year_path = os.path.join(EXAMS_PATH, year)
    if not os.path.isdir(year_path):
        return []
    return sorted(
        [
            f for f in os.listdir(year_path)
            if os.path.isfile(os.path.join(year_path, f)) and not f.startswith('.')
        ]
    )

# START command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        'Hello! I am your bot.',
        reply_markup = main_keyboard
    )
    

# HELP command
async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        f'Hello {update.effective_user.first_name}, I am here to assist you with WIUT Math Exam Samples.\nIf you need help, text to manager @marshallthethird.'
    )

# Show years
async def show_years(update: Update, context: ContextTypes.DEFAULT_TYPE):
    years = get_folder()
    keyboard = [[KeyboardButton(year)] for year in years]
    keyboard.append([KeyboardButton("⬅️ Main Menu")])
    await update.message.reply_text(
        "Select a year to view available exam files:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

# show files in the selected year
async def show_files(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    year = update.message.text
    if year not in get_folder():
        await update.message.reply_text(f"Year {year} not found. Please select from the list.")
        return

    context.user_data["selected_year"] = year
    files = get_exam_files(year)
    if not files:
        await update.message.reply_text(f"No exam files found for the year {year}.")
        return
    
    keyboard = [[KeyboardButton(year)] for year in files]
    keyboard.append([KeyboardButton("⬅️ Back")])
    #file_list = "\n".join(files)
    await update.message.reply_text(
        f"Exam files for {year}:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=False)
    )

# send the selected exam file
async def send_exam_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    filename = update.message.text
    selected_year = context.user_data.get('selected_year')
    if not selected_year:
        await update.message.reply_text("Please select a year first.")
        return
    
    year_path = os.path.join(EXAMS_PATH, selected_year, filename)
    if os.path.exists(year_path):
        await update.message.reply_document(
            document=open(year_path, 'rb')
        )
    else:
        await update.message.reply_text(f"File {filename} not found in year {selected_year}."
        )

# navig commands 
async def go_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await start(update, context)

async def go_to_years(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await show_years(update, context)

# commands list
app = ApplicationBuilder().token("7332463494:AAEGGzZ1_Ag8ptzpfJIXHGkPDl1_6SxZQ8g").build()

app.add_handler(CommandHandler("help", help))
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("WIUT Math Exam Samples"), show_years))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("Help"), help))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("⬅️ Main Menu"), go_to_main_menu))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("⬅️ Back"), go_to_years))
app.add_handler(MessageHandler(filters.TEXT & filters.Regex("^[0-9]{4}$"), show_files))
app.add_handler(MessageHandler(filters.TEXT, send_exam_file))

print("Bot is running...")
app.run_polling()