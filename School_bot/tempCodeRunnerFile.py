@dp.message_handler(state="support_answear_finish")
async def support_answear_finish(message: types.Message, state: FSMContext):
    text = message.text
    
    async with state.proxy() as data:
        user_id = data.get('user_id')
        message_id = data.get('message_id')
        
    await bot.send_message(chat_id=user_id,
                           text=text+"\n\nЗ повагою, English School Wuppertal.",
                           parse_mode="HTML")
    
    result = await processed_message(user_id, message_id)
    
    if result:
        await bot.send_message(chat_id=message.from_user.id,
                               text="<b>✅ Повідомлення опрацьовано!</b>",
                               parse_mode="HTML")
    
    else:
        await bot.send_message(chat_id=message.from_user.id,
                               text=f"<b>❌ Помилка! {ERRORS['NOT_DEFINED']}</b>",
                               parse_mode="HTML")
    
    await state.reset_state()