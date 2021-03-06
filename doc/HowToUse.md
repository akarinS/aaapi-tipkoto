[注意はこちら](https://github.com/akarinS/aaapi-tipkoto)

使い方
===

balance/残高
---

残高を確認します。

    @tipkotone balance

deposit/入金/address/アドレス
---

入金用アドレスを確認します。

    @tipkotone deposit

withdraw/出金
---

出金します。 手数料は0.0001KOTOです。  
出金額に all,全額 が使えます。  
ただし、zアドレスには出金できません。  

    @tipkotone withdraw ADDRESS 50
    @tipkotone withdraw ADDRESS all

tip/投げ銭/投銭/send/送金
---

投げ銭します。 手数料は0.0001KOTOです。  
投げ銭額には all,全額 が使えます。

    @tipkotone tip @screen_name 39 Thank you!

followme/フォローミー/フォローして
---

フォローします。

    @tipkotone followme

help/ヘルプ
---

このページに誘導します。

    @tipkoto help

FAQ
===

Q. 投げ銭でも0.0001KOTOの手数料がかかるのはどうして？  
A. KotoはZCashと同じくアカウント機能が無効化されており、moveコマンドが使えません。出金だけでなく投げ銭もz_sendmanyコマンドを使っているため、トランザクション手数料が発生します。  
  
Q. 投げ銭/出金を全額してないのに、直後の残高が一度0になるのはどうして？  
A. z_sendmanyコマンドで送金すると、送金していない残高もお釣りとして新たに生成されたお釣り用アドレスへ送金されてしまいます。
それを防ぐためにお釣りを元アドレスに送金しています。したがって、お釣りが承認中になり、残高が一時的に0になります。  
  
Q. この額では出金できません・・・と言われるのはどうして？  
A. Kotoの最小送金可能額は0.00000054KOTOです。送金額やお釣りが0.00000054KOTO未満にならないよう気をつけてください。  

Q. 待ち時間が長すぎたため中断されました・・・と言われるのはどうして？  
A. 連続での投げ銭を可能にするために、お釣りの承認を待つ処理があります。それが1時間を超えると中断します。  
  
Q. 寄付したい！  
A. ありがとう！ @tipkotoneに投げ銭すると寄付できます！  

