"use strict";

const { Contract } = require("fabric-contract-api");

class SmartEnergyContract extends Contract {
  /**
   * Фіксація еталонного хешу стану лічильника у розподіленому реєстрі.
   * @param {Context} ctx Контекст транзакції Hyperledger
   * @param {String} deviceId Ідентифікатор пристрою
   * @param {String} timestamp Час фіксації телеметрії
   * @param {String} dataHash SHA-256 хеш даних
   */
  async SaveStateHash(ctx, deviceId, timestamp, dataHash) {
    // Формування унікального композитного ключа.
    const recordKey = `${deviceId}_${timestamp}`;

    // Створення об'єкта структури для збереження в реєстрі.
    const stateRecord = {
      deviceId: deviceId,
      timestamp: Number.parseInt(timestamp, 10),
      dataHash: dataHash,
      docType: "stateHash",
    };

    // Перетворення об'єкта у буфер та виконання запису в незмінний реєстр (Ledger).
    const recordBuffer = Buffer.from(JSON.stringify(stateRecord));
    await ctx.stub.putState(recordKey, recordBuffer);

    console.info(`[BLOCKCHAIN] Записано незмінний хеш для ключа: ${recordKey}`);
    return JSON.stringify({ success: true, key: recordKey });
  }

  /**
   * Читання еталонного хешу з блокчейну для проведення аудиту цілісності.
   * @param {Context} ctx Контекст транзакції
   * @param {String} deviceId Ідентифікатор пристрою
   * @param {String} timestamp Час фіксації телеметрії
   */
  async GetStateHash(ctx, deviceId, timestamp) {
    // Формування композитного ключа пошуку.
    const recordKey = `${deviceId}_${timestamp}`;

    // Вилучення масиву байтів із розподіленого реєстру.
    const recordBytes = await ctx.stub.getState(recordKey);

    // Перевірка наявності запису в реєстрі.
    if (!recordBytes || recordBytes.length === 0) {
      throw new Error(`Запис для ключа ${recordKey} не знайдено в блокчейні`);
    }

    // Десеріалізація об'єкта JSON та повернення значення еталонного хешу.
    const record = JSON.parse(recordBytes.toString());
    return record.dataHash;
  }
}

module.exports.SmartEnergyContract = SmartEnergyContract;
module.exports.contracts = [SmartEnergyContract];
