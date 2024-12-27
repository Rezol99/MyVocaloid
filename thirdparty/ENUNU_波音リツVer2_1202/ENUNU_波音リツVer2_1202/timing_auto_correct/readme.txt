ENUNU自動タイミング補正　Ver.1.4.0 ENUNU0.3.1 モデル組み込み用


■使い方

ENUNUモデルのcharacter.txtとかが置いてあるフォルダに「timing_auto_correct」フォルダを設置し、enuconfigを以下のようなに書き換えてください。


    timing_editor: [
            "%e/extensions/velocity_applier.py",
            "%v/timing_auto_correct/enunu_timing_auto_correct.py",
        ] # default: null





■settings.txtについて

 ◆consonant_retio= の数値は子音がどれだけ1つ前の母音を侵食して良いか割合を指定するものです
  0.1～0.9の間で指定してください。
  デフォルトは0.42です。
  0.6に設定すると、例えばUST上で[か][し]、ラベル上で[k][a][sh][i]の時に、[sh]の長さが最大で[a]の長さの0.6倍(60％)まで食い込むことを許します。
  この設定は、短いノートの次にs,sh等長い子音が来る時に、値を小さくし過ぎると子音が弱くなり、大きくし過ぎると母音が弱くなります。
  0.4～0.7あたりが良い結果になりそうです。

 ◆a=～N=は先頭母音のラベル位置とリズム位置の差を吸収するためのものです
  デフォルト値として波音リツデータベースから平均を出した数値が入っています

 ◆using_consonant_list=　はonにすると子音の長さが consonant_time.txtの内容で固定されます。
  学習量が少ないデータベースを使う場合にはonにすると良い結果になる可能性があります
  子音長がしっかりしてるモデルの場合はoffにしてください
  私が公開しているconsonant_counter（https://drive.google.com/file/d/1gNQ-hSXBZ5bkaE3BOSSJIQ_SP7R4J_mW/view?usp=sharing）でDBから子音長を抜き出して使用することができます。
  最初から入っているデータは波音リツ歌声データベースVer.2から取得したものです。

 ◆consonant_scale=　は consonant_time の子音の長さを調整します。
  1.0で設定そのまま、1.1で1割子音が長く、0.8なら2割短くなります。
  曲のテンポなどに合わせて調整してみてください。

 ◆linkage= の数値は1にしてください。
  1にすると、--mono_scoreの次のオプションと--mono_timingの次のオプションをファイルパスとして読み込みます
  他のオプションは無視します
  --mono_timingの数値を書き換えてを上書き保存します




カノン
twitter: @canon_73
mail: canon7373@gmail.com
web: http://www.canon-voice.com/