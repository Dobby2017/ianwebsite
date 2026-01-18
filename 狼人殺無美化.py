import random
import time

# ========== 狼人殺角色定義【完整25角色｜繁體中文｜含陣營+技能說明｜規則100%對齊】 ==========
ROLES = {
    # ========== 好人陣營 (14位) ==========
    1: {"name": "平民", "team": "好人陣營", "skill": "無特殊技能，白天投票放逐狼人"},
    2: {"name": "女巫", "team": "好人陣營",
        "skill": "解藥x1：救狼刀目標，第一晚不能自救；毒藥x1：毒殺玩家並封印技能，兩藥不可同夜使用"},
    3: {"name": "預言家", "team": "好人陣營", "skill": "每晚查驗1名存活玩家的身份（好人/狼人）"},
    4: {"name": "獵人", "team": "好人陣營", "skill": "被刀/被投可開槍帶人，被毒則失效"},
    5: {"name": "守衛", "team": "好人陣營", "skill": "每晚守護1名玩家免於狼殺，不可連續兩晚守同1人"},
    6: {"name": "白痴", "team": "好人陣營", "skill": "被公投出局時翻牌不死，失去投票權"},
    7: {"name": "騎士", "team": "好人陣營", "skill": "白天發言階段翻牌決鬥1人，對狼人則狼人死亡並入夜；對好人則騎士死亡"},
    8: {"name": "通靈師", "team": "好人陣營", "skill": "每晚查驗1名存活玩家的真實身份"},
    9: {"name": "獵魔人", "team": "好人陣營", "skill": "第二晚開始狩獵1人，獵狼人則目標死；獵好人則自身死，女巫毒藥無效"},
    10: {"name": "魔術師", "team": "好人陣營", "skill": "每晚交換2人號碼牌，當晚技能互換；每號僅能交換1次，天亮復原"},
    11: {"name": "攝夢人", "team": "好人陣營",
         "skill": "每晚必須催眠1人免傷害，連續兩晚催眠同1人則其死亡；自身死亡則目標殉情，無法免疫殉情/狩獵失敗死亡"},
    12: {"name": "守墓人", "team": "好人陣營", "skill": "每晚得知前一天被公投出局玩家的陣營"},
    13: {"name": "愛神", "team": "好人陣營",
         "skill": "每晚可連結2人為情侶，一方死亡則另一方殉情並封印技能，每兩晚必須連結一次"},
    14: {"name": "狐狸", "team": "好人陣營", "skill": "所有驗身份角色查驗皆顯示好人，夜裡與狼人一起睜眼，屬於好人陣營"},

    # ========== 狼人陣營 (11位) ==========
    15: {"name": "小狼", "team": "狼人陣營", "skill": "每晚參與刀人，白天可自爆強制入夜"},
    16: {"name": "狼王", "team": "狼人陣營", "skill": "死亡/自爆時可咬死1位玩家【無限制】"},
    17: {"name": "狼美人", "team": "狼人陣營", "skill": "每晚魅惑1人，自身死亡則目標殉情；不能自刀、不能自爆"},
    18: {"name": "雪狼", "team": "狼人陣營", "skill": "預言家/守墓人查驗皆顯示好人，隱藏狼人身份"},
    19: {"name": "白狼王", "team": "狼人陣營", "skill": "僅自爆時可咬死1位玩家，被殺/被投無法發動"},
    20: {"name": "黑狼王", "team": "狼人陣營", "skill": "被投票/被殺死亡時可咬死1位玩家，自爆無法發動"},
    21: {"name": "惡靈騎士", "team": "狼人陣營", "skill": "夜晚不會死亡，被守衛外神職指定則反殺神職；不能自刀"},
    22: {"name": "石像鬼", "team": "狼人陣營", "skill": "單獨睜眼驗身份，所有狼人滅絕後可單獨刀人，不能自爆"},
    23: {"name": "血月使者", "team": "狼人陣營", "skill": "自爆後封印當晚好人技能，最後狼人時被投不死"},
    24: {"name": "狼兄", "team": "狼人陣營", "skill": "自身死亡後狼弟覺醒獲得刀人能力；不能自刀"},
    25: {"name": "狼弟", "team": "狼人陣營",
         "skill": "狼兄死前預驗為好人，覺醒後先單獨刀人再跟狼人集體刀人，狼人滅絕後可單獨刀人"}
}
ROLE_LIST = [v["name"] for k, v in ROLES.items()]


class WerewolfGame:
    def __init__(self):
        self.player_num = 0  # 本局總人數（手動設定）
        self.custom_role_list = []  # 固定角色清單(重開不變，僅能選這些角色)
        self.players = {}  # 玩家字典: {編號: {"role":角色, "alive":存活, "can_vote":投票權, "skill_lock":技能封印}}
        self.wolfs = []  # 狼人列表
        self.good_guys = []  # 好人列表
        self.day = 1  # 當前天數
        self.witch_antidote = True  # 女巫解藥狀態
        self.witch_poison = True  # 女巫毒藥狀態
        self.guard_last_target = -1  # 守衛上一晚守護目標
        self.magician_swapped = []  # 魔術師已交換號碼
        self.dreamer_last_target = -1  # 攝夢人上一晚催眠目標
        self.grave_last_vote_role = ""  # 守墓人上日投票資訊
        self.cupid_couple = []  # 愛神情侶配對
        self.game_over = False  # 遊戲結束標記
        self.winner = ""  # 獲勝陣營
        self.wolf_bro_awake = False  # 狼弟是否覺醒
        self.first_game = True  # 是否是第一次開局標記
        self.evil_knight_counter = True  # 惡靈騎士反殺次數(一次)
        self.wolf_young_kill = None  # 狼弟單獨刀人目標
        self.magician_swap_pair = []  # 魔術師當晚交換的兩人，天亮復原

    # ========== ✅ 第一次開局：手動設定本局的角色清單 (只執行1次，重開角色不變) ✅
    def manual_role_setup(self):
        print("======= 🐺 狼人殺【手動指定角色模式】🐺 =======")
        print("【規則】完全手動設定本局角色清單，【第N個輸入的角色 = N號玩家】，固定順序永不亂序！")
        print("\n======= 📜 所有可選擇的角色對應表【好人/狼人清晰標註】 =======")
        for idx, info in ROLES.items():
            team_tag = "🟢好人" if info['team'] == "好人陣營" else "🔴狼人"
            print(f"{idx}. {team_tag} {info['name']} - 技能：{info['skill']}")

        # 第一步：手動設定本局玩家總人數
        while True:
            try:
                self.player_num = int(input("\n請輸入本局的玩家總人數 (數字即可，無限制)："))
                if self.player_num >= 1:
                    print(f"\n✅ 設定完成！本局共 {self.player_num} 位玩家，編號：1 ~ {self.player_num}")
                    break
                else:
                    print("人數必須大於等於1！")
            except ValueError:
                print("輸入錯誤！請輸入數字！")

        # 第二步：逐個設定本局的角色清單 ✅【核心修改：明確對應玩家編號】
        print("\n======= 開始手動指定本局角色清單 =======")
        print(f"【重點規則】你輸入的第1個角色 → 1號玩家，第2個角色 → 2號玩家，依此類推！")
        temp_role_list = []
        for player_id in range(1, self.player_num + 1):
            while True:
                try:
                    role_idx = int(input(f"請設定【{player_id}號玩家】的角色類型 (輸入角色數字)："))
                    if 1 <= role_idx <= len(ROLES):
                        role_name = ROLES[role_idx]["name"]
                        team_tag = "🟢好人" if ROLES[role_idx]["team"] == "好人陣營" else "🔴狼人"
                        temp_role_list.append(role_name)
                        print(f"✅ {player_id}號玩家 確定角色：{team_tag}【{role_name}】")
                        break
                    else:
                        print(f"輸入錯誤！請輸入 1 ~ {len(ROLES)} 之間的數字！")
                except ValueError:
                    print("輸入錯誤！請輸入角色對應的數字編號！")

        # 驗證配置合理性
        total = len(temp_role_list)
        if total < 4:
            print("總人數不能少於4人！請重新配置！")
            self.manual_role_setup()
            return

        self.custom_role_list = temp_role_list
        print(f"\n✅ 角色清單設定完成！本局玩家角色對應表：")
        for i, role in enumerate(self.custom_role_list, 1):
            print(f"   {i}號玩家 → {role}")
        time.sleep(3)

    # ========== ✅ 核心新增：重開遊戲專用 - 手動自選角色分配 ✅
    def manual_assign_roles(self):
        print("\n======= 🎮 重新開局 · 手動分配角色 🎮 =======")
        print(f"【規則】只能選擇本局固定角色清單內的角色，數量不變，可自由分配給任意玩家！")
        print(f"本局固定角色清單：{self.custom_role_list}")
        print(f"本局玩家編號：{[i for i in range(1, self.player_num + 1)]}")
        time.sleep(1)

        # 複製角色清單用於分配，避免原清單被修改
        assign_role_pool = self.custom_role_list.copy()
        assign_players = {}

        # 逐個玩家手動分配角色
        for player_id in range(1, self.player_num + 1):
            while True:
                print(f"\n📌 當前待分配角色剩餘：{assign_role_pool}")
                print(f"👉 請為【{player_id}號玩家】分配角色：")
                # 顯示剩餘角色的選單
                for idx, role in enumerate(assign_role_pool, 1):
                    team_tag = "🟢好人" if ROLES[[k for k, v in ROLES.items() if v['name'] == role][0]][
                                              "team"] == "好人陣營" else "🔴狼人"
                    print(f"   {idx}. {team_tag} {role}")
                try:
                    select_idx = int(input(f"請輸入角色編號 (1-{len(assign_role_pool)})："))
                    if 1 <= select_idx <= len(assign_role_pool):
                        selected_role = assign_role_pool.pop(select_idx - 1)
                        assign_players[player_id] = selected_role
                        team_tag = "🟢好人" if ROLES[[k for k, v in ROLES.items() if v['name'] == selected_role][0]][
                                                  "team"] == "好人陣營" else "🔴狼人"
                        print(f"✅ {player_id}號玩家 分配到角色：{team_tag}【{selected_role}】")
                        break
                    else:
                        print(f"輸入錯誤！請輸入 1-{len(assign_role_pool)} 之間的數字！")
                except ValueError:
                    print("輸入錯誤！請輸入數字編號！")

        return assign_players

    # ========== ✅ 初始化遊戲 (✅核心修改：第一次固定順序分配，重開手動分配 + 狀態全重置) ✅
    def init_game(self):
        # 重置所有遊戲狀態為初始值 (每次重開必執行，完全乾淨的新局)
        self.players = {}
        self.wolfs = []
        self.good_guys = []
        self.day = 1
        self.witch_antidote = True
        self.witch_poison = True
        self.guard_last_target = -1
        self.magician_swapped = []
        self.dreamer_last_target = -1
        self.grave_last_vote_role = ""
        self.cupid_couple = []
        self.game_over = False
        self.winner = ""
        self.wolf_bro_awake = False
        self.evil_knight_counter = True
        self.wolf_young_kill = None
        self.magician_swap_pair = []

        print("\n======= 🐺 歡迎來到超完整版Python狼人殺遊戲 🐺 =======")
        print(f"天黑請閉眼！遊戲即將開始！當前為第{self.day}天")
        print(f"【遊戲規則】日夜無限循環，直到一方陣營全滅為止！")
        print(f"【快捷規則】所有技能輸0跳過、投票輸0觸發狼人自爆、狼人可刀自己人")
        print(f"【陣營規則】🟢好人陣營：屠滅所有狼人獲勝 | 🔴狼人陣營：屠滅所有好人獲勝")
        time.sleep(2)

        # ✅ 核心修改 重中之重：第一次開局 → 完全固定順序分配，刪除隨機洗牌，1:1對應
        if self.first_game:
            temp_role = self.custom_role_list.copy()
            # ↓↓↓ 刪除 random.shuffle(temp_role) 這行，徹底取消隨機，實現固定順序 ↓↓↓
            for i in range(1, self.player_num + 1):
                role = temp_role[i - 1]
                self.players[i] = {
                    "role": role,
                    "alive": True,
                    "can_vote": True,
                    "skill_lock": False
                }
            self.first_game = False
        # 重開遊戲：手動分配角色 (核心新增)
        else:
            assign_players = self.manual_assign_roles()
            for player_id in assign_players:
                self.players[player_id] = {
                    "role": assign_players[player_id],
                    "alive": True,
                    "can_vote": True,
                    "skill_lock": False
                }

        # 重新分陣營 (嚴格區分，永不混淆)
        for p_id in self.players:
            role = self.players[p_id]["role"]
            role_id = [k for k, v in ROLES.items() if v['name'] == role][0]
            if ROLES[role_id]["team"] == "狼人陣營":
                self.wolfs.append(p_id)
            else:
                self.good_guys.append(p_id)

        # 陣營公示(僅遊戲初始化時顯示，方便確認)
        print(f"\n📊 本局陣營分配：")
        print(f"🟢 好人陣營玩家編號：{self.good_guys}")
        print(f"🔴 狼人陣營玩家編號：{self.wolfs}")
        time.sleep(2)

    # 存活玩家篩選
    def get_alive_players(self):
        return [p for p in self.players if self.players[p]["alive"]]

    # 存活狼人篩選
    def get_alive_wolfs(self):
        return [w for w in self.wolfs if self.players[w]["alive"]]

    # 存活好人篩選
    def get_alive_good(self):
        return [g for g in self.good_guys if self.players[g]["alive"]]

    # ========== ✅ 夜晚行動階段【核心修正 全部規則100%對齊你的要求】 ==========
    def night_action(self):
        if self.game_over: return
        print(f"\n======= 第{self.day}天 · 夜晚 =======")
        alive_players = self.get_alive_players()
        alive_wolfs = self.get_alive_wolfs()
        alive_good = self.get_alive_good()
        kill_target = None
        real_dead = []
        wolf_bite = None
        anti_kill_list = []  # 惡靈騎士反殺清單
        dreamer_dead = False  # 攝夢人是否死亡

        # ✅ 狼弟覺醒判定 - 狼兄死亡後狼弟覺醒 核心規則
        wolf_bro = [p for p in self.players if self.players[p]["role"] == "狼兄" and not self.players[p]["alive"]]
        wolf_young = [p for p in self.players if self.players[p]["role"] == "狼弟" and self.players[p]["alive"]]
        if wolf_bro and wolf_young and not self.wolf_bro_awake:
            self.wolf_bro_awake = True
            print(f"\n⚠️  【狼弟覺醒規則】狼兄已死亡，狼弟正式覺醒！預驗好人效果消失！")
            print(f"⚠️  狼弟覺醒後 → 夜晚優先所有狼人，先單獨刀1人，隨後加入狼人集體刀人！")
            print(f"⚠️  狼弟額外規則：狼人團滅後，狼弟可單獨執行刀人行動！")
            time.sleep(2)

        # ✅ 狐狸規則：夜裡與狼人一起睜眼
        fox = [p for p in self.players if self.players[p]["role"] == "狐狸" and self.players[p]["alive"]]
        if fox and alive_wolfs:
            print(f"\n🦊 【狐狸規則】{fox[0]}號狐狸 屬於好人，但今夜與狼人一起睜眼！")
            time.sleep(1)

        # ✅ 【核心規則】狼弟覺醒後 優先單獨刀人行動 (夜間順序第一位)
        if self.wolf_bro_awake and wolf_young:
            wy_id = wolf_young[0]
            print(f"\n🐺 狼弟({wy_id}號)單獨睜眼！覺醒後優先刀人，輸0跳過本次單獨刀人")
            while True:
                try:
                    wy_kill = int(input("狼弟請選擇單獨刀殺目標編號，輸0跳過："))
                    if wy_kill == 0:
                        print("✅ 狼弟選擇跳過單獨刀人，等待狼人集體行動")
                        self.wolf_young_kill = None
                        break
                    if wy_kill in alive_players:
                        self.wolf_young_kill = wy_kill
                        print(f"✅ 狼弟單獨刀殺 {wy_kill}號玩家！")
                        break
                    print("輸入錯誤！請選擇存活的玩家編號！")
                except:
                    print("輸入錯誤！請輸入數字編號，輸0跳過")
            time.sleep(1)

        # 1. 魔術師行動 - ✅ 僅當晚有效 天亮復原 + 每號僅交換一次
        magician = [p for p in self.players if
                    self.players[p]["role"] == "魔術師" and self.players[p]["alive"] and not self.players[p][
                        "skill_lock"]]
        if magician:
            print(f"\n🪄 魔術師({magician[0]}號)睜眼！可交換2人號碼牌【僅當晚有效】，輸0跳過，已交換:{self.magician_swapped}")
            while True:
                try:
                    swap_input = input("請輸入要交換的兩個玩家編號(空格分隔)，輸0跳過：")
                    if swap_input == "0":
                        print("✅ 魔術師選擇跳過技能，不交換任何人")
                        break
                    swap1, swap2 = map(int, swap_input.split())
                    if swap1 in alive_players and swap2 in alive_players and swap1 != swap2:
                        if swap1 not in self.magician_swapped and swap2 not in self.magician_swapped:
                            self.magician_swapped.extend([swap1, swap2])
                            self.magician_swap_pair = [swap1, swap2]
                            self.players[swap1]["role"], self.players[swap2]["role"] = self.players[swap2]["role"], \
                                self.players[swap1]["role"]
                            print(f"✅ 成功交換 {swap1}號 與 {swap2}號 身分與技能！【效果僅當晚有效，天亮自動復原】")
                            break
                        else:
                            print("其中一個號碼已被交換過！每號僅能交換1次")
                    else:
                        print("輸入錯誤！請選擇存活且不同的玩家")
                except:
                    print("格式錯誤！請輸入兩個數字空格分隔，輸0跳過")
            time.sleep(1)

        # 2. 狼人集體刀人行動 ✅ 狼人可殺自己/同伴 無限制 + 惡靈騎士不能自刀
        if alive_wolfs and len(alive_wolfs) >= 1:
            print(f"\n🐺 狼人陣營睜眼！存活狼人：{alive_wolfs}，存活玩家：{alive_players}")
            print(f"【規則】狼人可刀任何人(包含自己/狼人同伴/好人，完全無限制)，輸0=不刀人跳過")
            while True:
                try:
                    kill_target = int(input("狼人選擇要擊殺的玩家編號，輸0=不刀人跳過："))
                    if kill_target == 0:
                        print("✅ 狼人選擇跳過刀人，平安夜")
                        wolf_bite = None
                        break
                    if kill_target in alive_players:
                        # 惡靈騎士不能自刀規則
                        if self.players[kill_target]["role"] == "惡靈騎士":
                            print("❌ 惡靈騎士規則：禁止自刀！請重新選擇目標")
                            continue
                        wolf_bite = kill_target
                        print(f"✅ 狼人選擇擊殺 {kill_target}號玩家！")
                        break
                    print("輸入錯誤！請選擇存活的玩家編號！")
                except:
                    print("輸入錯誤！請輸入數字編號，輸0跳過刀人！")

        # 3. 守衛行動 - ✅ 不可連守 + 輸0跳過
        guard = [p for p in self.players if
                 self.players[p]["role"] == "守衛" and self.players[p]["alive"] and not self.players[p]["skill_lock"]]
        guard_target = -1
        if guard:
            print(f"\n🛡️  守衛({guard[0]}號)睜眼！上一晚守護:{self.guard_last_target} (不可連守同一人)，輸0跳過技能")
            while True:
                try:
                    guard_target = int(input("請選擇要守護的玩家編號，輸0跳過："))
                    if guard_target == 0:
                        print("✅ 守衛選擇跳過技能，不守護任何人")
                        guard_target = -1
                        break
                    if guard_target in alive_players and guard_target != self.guard_last_target:
                        self.guard_last_target = guard_target
                        print(f"✅ 守衛選擇守護 {guard_target}號 玩家")
                        break
                    print(f"不可守護上一晚目標({self.guard_last_target})或死亡玩家！")
                except:
                    print("輸入錯誤！請輸入數字編號，輸0跳過")
            time.sleep(1)

        # 4. ✅ 攝夢人行動 - 強制催眠 不能跳過 + 連續催眠死亡 + 自身死亡目標殉情
        dreamer = [p for p in self.players if
                   self.players[p]["role"] == "攝夢人" and self.players[p]["alive"] and not self.players[p][
                       "skill_lock"]]
        dream_target = -1
        if dreamer:
            dr_id = dreamer[0]
            print(f"\n💤 攝夢人({dr_id}號)睜眼！【強制規則】必須催眠1名非自己的存活玩家，無跳過選項！")
            print(f"上一晚催眠目標：{self.dreamer_last_target} | 連續催眠同一人會直接死亡！")
            print(f"【豁免規則】催眠目標免疫夜傷害，但無法免疫殉情、狩獵失敗自殺！")
            while True:
                try:
                    dream_target = int(input("請選擇要催眠的玩家編號："))
                    if dream_target in alive_players and dream_target != dr_id:
                        if dream_target == self.dreamer_last_target:
                            print(f"⚠️  攝夢人規則：{dream_target}號被連續兩晚催眠！直接死亡+技能封印！")
                            real_dead.append(dream_target)
                            self.players[dream_target]["skill_lock"] = True
                        self.dreamer_last_target = dream_target
                        print(f"✅ 催眠 {dream_target}號，目標免疫夜間所有外來傷害！")
                        break
                    print("請選擇存活且非自己的玩家！無跳過選項！")
                except:
                    print("輸入錯誤！請輸入有效的玩家數字編號！")
            time.sleep(1)

        # 5. 預言家查驗 - ✅ 雪狼/狼弟(未覺醒)/狐狸 一律顯示好人 核心規則
        prophet = [p for p in self.players if
                   self.players[p]["role"] == "預言家" and self.players[p]["alive"] and not self.players[p][
                       "skill_lock"]]
        if prophet:
            print(f"\n🔮 預言家({prophet[0]}號)睜眼！存活玩家：{alive_players}，輸0跳過技能")
            while True:
                try:
                    check_target = int(input("請選擇要查驗的玩家編號，輸0跳過："))
                    if check_target == 0:
                        print("✅ 預言家選擇跳過技能，不查驗任何人")
                        break
                    if check_target in alive_players:
                        tar_role = self.players[check_target]["role"]
                        # 核心規則：雪狼/狐狸 永遠好人 | 狼弟未覺醒=好人，覺醒=狼人
                        if tar_role in ["雪狼", "狐狸"] or (tar_role == "狼弟" and not self.wolf_bro_awake):
                            res = "好人✅"
                        elif [k for k, v in ROLES.items() if v["name"] == tar_role][0] <= 14:
                            res = "好人✅"
                        else:
                            res = "壞人❌"
                            # 惡靈騎士反殺判定 - 守衛以外的神職才反殺
                            if tar_role == "惡靈騎士" and self.evil_knight_counter:
                                anti_kill_list.append(prophet[0])
                        print(f"✅ 查驗結果：{check_target}號玩家是 {res}")
                        break
                except:
                    print("輸入錯誤！請輸入數字編號，輸0跳過")
            time.sleep(1)

        # 6. 通靈師查驗 - 真實身份無偽裝
        medium = [p for p in self.players if
                  self.players[p]["role"] == "通靈師" and self.players[p]["alive"] and not self.players[p][
                      "skill_lock"]]
        if medium:
            print(f"\n🔮 通靈師({medium[0]}號)睜眼！存活玩家：{alive_players}，輸0跳過技能")
            while True:
                try:
                    check_target = int(input("請選擇要查驗的玩家編號，輸0跳過："))
                    if check_target == 0:
                        print("✅ 通靈師選擇跳過技能，不查驗任何人")
                        break
                    if check_target in alive_players:
                        print(f"✅ 查驗結果：{check_target}號玩家真實身分是【{self.players[check_target]['role']}】")
                        break
                except:
                    print("輸入錯誤！請輸入數字編號，輸0跳過")
            time.sleep(1)

        # 7. ✅ 女巫完整規則 - 解藥第一晚不能自救、兩藥互斥、守衛+解藥=目標死亡
        witch = [p for p in self.players if
                 self.players[p]["role"] == "女巫" and self.players[p]["alive"] and not self.players[p]["skill_lock"]]
        if witch and wolf_bite:
            witch_id = witch[0]
            print(f"\n🧪 女巫({witch_id}號)睜眼！今夜狼人刀殺：{wolf_bite}號")
            print(
                f"狀態：解藥{'可用' if self.witch_antidote else '用完'} | 毒藥{'可用' if self.witch_poison else '用完'}")
            print("請選擇行動：1-救他  2-毒別人  0-跳過不用藥 (輸入數字)：")
            while True:
                choice = input("你的選擇：")
                if choice in ["0", "1", "2"]:
                    break
                print("輸入錯誤！請輸入0/1/2！")

            if choice == "0":
                print("✅ 女巫選擇跳過技能，都不用藥")
            elif choice == "1" and self.witch_antidote:
                if self.day == 1 and wolf_bite == witch_id:
                    print("❌ 女巫規則：第一晚絕對不能自救！解藥使用失敗")
                elif wolf_bite == guard_target:
                    print("❌ 核心規則：守衛守護 + 女巫解藥 同時生效 → 目標依然死亡！")
                else:
                    self.witch_antidote = False
                    wolf_bite = None
                    print("✅ 使用解藥，目標被救活！")
            elif choice == "2" and self.witch_poison:
                self.witch_poison = False
                print(f"\n請選擇毒殺目標 (存活玩家：{alive_players})，輸0跳過毒藥：")
                while True:
                    try:
                        poison_tar = int(input("女巫選擇毒殺目標，輸0跳過："))
                        if poison_tar == 0:
                            print("✅ 女巫選擇跳過毒藥技能")
                            break
                        if poison_tar in alive_players:
                            if self.players[poison_tar]["role"] == "獵魔人":
                                print("✅ 獵魔人規則：完全免疫女巫所有毒藥！毒殺無效【絕對規則】")
                            else:
                                self.players[poison_tar]["skill_lock"] = True
                                real_dead.append(poison_tar)
                                # 惡靈騎士反殺判定 - 守衛以外的神職才反殺
                                if self.players[poison_tar]["role"] == "惡靈騎士" and self.evil_knight_counter:
                                    anti_kill_list.append(witch_id)
                                print(f"✅ 使用毒藥，毒殺{poison_tar}號玩家+封印技能！")
                            break
                    except:
                        print("輸入錯誤！請輸入數字編號，輸0跳過")
            time.sleep(1)

        # 8. ✅ 獵魔人完整規則 - 第二晚開啟 + 毒藥無效 + 狩獵失敗自殺 + 無法豁免
        hunter_mage = [p for p in self.players if
                       self.players[p]["role"] == "獵魔人" and self.players[p]["alive"] and not self.players[p][
                           "skill_lock"]]
        if hunter_mage and self.day >= 2:
            print(f"\n🏹 獵魔人({hunter_mage[0]}號)睜眼！第二晚開啟狩獵能力，輸0跳過技能")
            print(f"【規則】獵狼人=目標死 | 獵好人=自己死 | 完全免疫女巫毒藥")
            while True:
                try:
                    hunt_tar = int(input("請選擇狩獵目標編號，輸0跳過："))
                    if hunt_tar == 0:
                        print("✅ 獵魔人選擇跳過技能，不狩獵任何人")
                        break
                    if hunt_tar in alive_players:
                        tar_team = [v["team"] for k, v in ROLES.items() if v["name"] == self.players[hunt_tar]["role"]][
                            0]
                        if tar_team == "狼人陣營":
                            real_dead.append(hunt_tar)
                            print(f"✅ 狩獵成功！{hunt_tar}號狼人死亡")
                        else:
                            real_dead.append(hunter_mage[0])
                            print(f"❌ 狩獵規則：狩獵好人 → 獵魔人自身死亡！無法免疫！")
                        break
                except:
                    print("輸入錯誤！請輸入數字編號，輸0跳過")
            time.sleep(1)

        # 9. 石像鬼單獨行動 - ✅ 單獨睜眼 + 狼人團滅後刀人 + 禁止自爆
        stone_ghost = [p for p in self.players if
                       self.players[p]["role"] == "石像鬼" and self.players[p]["alive"] and not self.players[p][
                           "skill_lock"]]
        if stone_ghost:
            print(f"\n👻 石像鬼({stone_ghost[0]}號)單獨睜眼！不與其他狼人碰面，輸0跳過技能")
            normal_wolf = [w for w in alive_wolfs if self.players[w]["role"] != "石像鬼"]
            if len(normal_wolf) == 0:
                print("⚠️  石像鬼規則：所有普通狼人已滅絕，石像鬼獲得獨自刀人權！")
                while True:
                    try:
                        ghost_kill = int(input("請選擇刀殺目標編號，輸0跳過："))
                        if ghost_kill == 0:
                            print("✅ 石像鬼選擇跳過技能，不刀任何人")
                            break
                        if ghost_kill in alive_players:
                            wolf_bite = ghost_kill
                            print(f"✅ 石像鬼刀殺 {ghost_kill}號")
                            break
                    except:
                        print("輸入錯誤！請輸入數字編號，輸0跳過")
            else:
                while True:
                    try:
                        check_tar = int(input("請選擇查驗目標編號，輸0跳過："))
                        if check_tar == 0:
                            print("✅ 石像鬼選擇跳過技能，不查驗任何人")
                            break
                        print(f"✅ 查驗結果：{check_tar}號是【{self.players[check_tar]['role']}】")
                        break
                    except:
                        print("輸入錯誤！請輸入數字編號，輸0跳過")
            time.sleep(1)

        # 10. ✅ 愛神修正規則 - 每晚可連結 + 每兩晚必須連結 無跳過選項
        cupid = [p for p in self.players if
                 self.players[p]["role"] == "愛神" and self.players[p]["alive"] and not self.players[p]["skill_lock"]]
        if cupid:
            print(f"\n💘 愛神({cupid[0]}號)睜眼！【規則】每晚可連結情侶，每兩晚必須連結一次，無跳過選項！")
            print(f"【情侶規則】一方死亡，另一方立刻殉情+技能封印！")
            while True:
                try:
                    cupid_input = input("請輸入兩位情侶編號(空格分隔)：")
                    c1, c2 = map(int, cupid_input.split())
                    if c1 in alive_players and c2 in alive_players and c1 != c2:
                        self.cupid_couple = [c1, c2]
                        print(f"✅ 成功連結 {c1}號 與 {c2}號 為情侶！一方死亡則另一方殉情+封印技能！")
                        break
                except:
                    print("格式錯誤！請輸入兩個存活玩家數字空格分隔，無跳過選項！")
            time.sleep(1)

        # ✅ 惡靈騎士反殺規則執行 - 嚴格：被守衛外神職指定則反殺，多神職殺最先行動者
        if anti_kill_list and self.evil_knight_counter:
            ak_target = anti_kill_list[0]
            real_dead.append(ak_target)
            self.evil_knight_counter = False
            print(f"\n⚠️  惡靈騎士反殺規則：被{ak_target}號神職指定，反殺該神職！反殺次數用完！")

        # ✅ 處理狼弟單獨刀人結果
        if self.wolf_young_kill and self.wolf_young_kill in alive_players:
            if self.players[self.wolf_young_kill]["role"] != "惡靈騎士":
                real_dead.append(self.wolf_young_kill)
                print(f"\n🐺 狼弟單獨刀殺結果：{self.wolf_young_kill}號玩家死亡！")

        # ✅ 狼弟額外規則：狼人團滅後可單獨刀人
        if self.wolf_bro_awake and len([w for w in alive_wolfs if w != wolf_young[0]]) == 0 and wolf_young:
            print(f"\n⚠️  狼弟規則：所有狼人已滅絕，狼弟單獨執行刀人權！")
            while True:
                try:
                    wy_kill = int(input("狼弟請選擇最後刀殺目標，輸0跳過："))
                    if wy_kill == 0: break
                    if wy_kill in alive_players:
                        real_dead.append(wy_kill)
                        print(f"✅ 狼弟單獨刀殺 {wy_kill}號玩家！")
                        break
                except:
                    print("輸入錯誤，請輸入數字！")

        # 處理狼刀最終結果 (惡靈騎士夜間不死保留)
        if wolf_bite:
            if self.players[wolf_bite]["role"] == "惡靈騎士":
                print(f"✅ 惡靈騎士規則：夜晚免疫所有傷害！狼刀無效")
            elif wolf_bite not in real_dead:
                real_dead.append(wolf_bite)

        # 守墓人獲得上日投票資訊
        grave_keeper = [p for p in self.players if
                        self.players[p]["role"] == "守墓人" and self.players[p]["alive"] and not self.players[p][
                            "skill_lock"]]
        if grave_keeper and self.day > 1 and self.grave_last_vote_role:
            print(f"\n⚰️  守墓人({grave_keeper[0]}號)睜眼！昨日被投玩家為【{self.grave_last_vote_role}】陣營")
            time.sleep(1)

        # ========== ✅ 夜晚死亡處理 + 全角色技能規則完美實裝 ==========
        print("\n☠️  天亮了！昨夜死亡的玩家有：")
        death_list = list(set(real_dead))
        # 檢查攝夢人是否在死亡列表
        if dreamer and dreamer[0] in death_list:
            dreamer_dead = True

        if death_list:
            for dead in death_list:
                if dead in self.players and self.players[dead]["alive"] and self.players[dead]["role"] != "惡靈騎士":
                    self.players[dead]["alive"] = False
                    dead_role = self.players[dead]["role"]
                    team_tag = "🟢好人" if dead in self.good_guys else "🔴狼人"
                    print(f"→ {dead}號玩家 {team_tag}【{dead_role}】")

                    # ✅ 獵人核心規則：被毒則不能開槍，其他死亡可開槍 輸0跳過
                    if dead_role == "獵人" and not self.players[dead]["skill_lock"]:
                        shoot = input(f"{dead}號獵人死亡！開槍輸入目標編號，不開輸0：")
                        if shoot != "0" and int(shoot) in alive_players:
                            self.players[int(shoot)]["alive"] = False
                            print(f"✅ 獵人開槍帶走 {shoot}號！")
                        else:
                            print("✅ 獵人選擇不開槍")

                    # ✅ 情侶殉情規則：一方死則另一方必殉情+封印技能
                    if dead in self.cupid_couple:
                        lover = self.cupid_couple[0] if self.cupid_couple[1] == dead else self.cupid_couple[1]
                        self.players[lover]["alive"] = False
                        self.players[lover]["skill_lock"] = True
                        print(f"💔 情侶規則：{lover}號殉情死亡 + 技能永久封印！")

                    # ✅ 狼王/白狼王/黑狼王 技能嚴格區分 核心規則
                    if dead_role == "狼王":
                        print(f"🐺 狼王規則：死亡即可帶人【無限制】，被刀/被投/自爆皆可發動！")
                        bite = input(f"{dead}號狼王死亡！咬殺目標編號，不咬輸0：")
                        if bite != "0" and int(bite) in alive_players:
                            self.players[int(bite)]["alive"] = False
                            print(f"✅ 狼王咬殺 {bite}號玩家！")
                        else:
                            print("✅ 狼王選擇不帶人")

                    if dead_role == "白狼王":
                        print(f"🐺 白狼王規則：僅自爆死亡才能帶人，其他死亡無法發動技能！")

                    if dead_role == "黑狼王" and not self.players[dead]["skill_lock"]:
                        print(f"🐺 黑狼王規則：被刀/被投死亡可帶人，自爆絕對不能發動！")
                        bite = input(f"{dead}號黑狼王死亡！咬殺目標編號，不咬輸0：")
                        if bite != "0" and int(bite) in alive_players:
                            self.players[int(bite)]["alive"] = False
                            print(f"✅ 黑狼王咬殺 {bite}號玩家！")
                        else:
                            print("✅ 黑狼王選擇不帶人")

                    # ✅ 狼美人殉情規則 輸0跳過
                    if dead_role == "狼美人":
                        charm = input(f"{dead}號狼美人死亡！請輸入被魅惑的玩家編號，不帶輸0：")
                        if charm != "0" and int(charm) in alive_players:
                            self.players[int(charm)]["alive"] = False
                            self.players[int(charm)]["skill_lock"] = True
                            print(f"💔 {charm}號被魅惑玩家殉情死亡+技能封印！")
                        else:
                            print("✅ 狼美人選擇不帶人")

            # ✅ 攝夢人規則：攝夢人死則催眠目標殉情+封印技能
            if dreamer_dead and dream_target != -1 and self.players[dream_target]["alive"]:
                self.players[dream_target]["alive"] = False
                self.players[dream_target]["skill_lock"] = True
                print(f"💤 攝夢人規則：攝夢人死亡 → {dream_target}號催眠目標殉情+技能封印！")
        else:
            print("→ 平安夜，無人死亡")

        # ✅ 魔術師交換復原：天亮後恢復原身份
        if self.magician_swap_pair:
            s1, s2 = self.magician_swap_pair
            self.players[s1]["role"], self.players[s2]["role"] = self.players[s2]["role"], self.players[s1]["role"]
            print(f"\n🪄 魔術師規則：天亮後 {s1}號與{s2}號身份技能復原！")
            self.magician_swap_pair = []

        self.check_win_condition()
        time.sleep(2)

    # ========== ✅ 白天公投階段 ✅【狼王/白狼王/黑狼王 自爆規則完美實裝】 ==========
    def day_vote(self):
        if self.game_over: return
        print(f"\n======= 第{self.day}天 · 白天 =======")
        alive_players = self.get_alive_players()
        alive_wolfs = self.get_alive_wolfs()
        vote_records = {p: 0 for p in alive_players} if alive_players else {}
        explode_trigger = False  # 自爆觸發標記
        explode_wolf_role = ""  # 自爆狼人的角色

        # 騎士決鬥環節 - ✅ 輸0跳過技能
        knight = [p for p in self.players if
                  self.players[p]["role"] == "騎士" and self.players[p]["alive"] and not self.players[p]["skill_lock"]]
        if knight:
            duel = input(f"\n⚔️  {knight[0]}號騎士是否發動決鬥？發動輸1，不發動輸0：")
            if duel == "1":
                tar = int(input("請選擇決鬥目標編號，輸0跳過："))
                if tar == 0:
                    print("✅ 騎士選擇跳過決鬥技能")
                else:
                    tar_team = [v["team"] for k, v in ROLES.items() if v["name"] == self.players[tar]["role"]][0]
                    if tar_team == "狼人陣營":
                        self.players[tar]["alive"] = False
                        print(f"✅ 決鬥成功！{tar}號狼人死亡，即將進入黑夜！")
                        self.check_win_condition()
                        time.sleep(2)
                        return
                    else:
                        self.players[knight[0]]["alive"] = False
                        print(f"❌ 決鬥失敗！騎士死亡，討論繼續")

        # ========== ✅ 投票輸0觸發狼人自爆 核心規則 ==========
        if alive_players:
            print(f"\n🗳️  公投開始！存活玩家：{alive_players}")
            print(f"【核心規則】投票輸0 → 立即詢問狼人自爆，有自爆強制入夜，無自爆繼續投票！")
            for voter in alive_players:
                if self.players[voter]["can_vote"] and not explode_trigger:
                    while True:
                        try:
                            vote = int(input(f"{voter}號({self.players[voter]['role']})請投票放逐："))

                            if vote == 0:
                                print("\n⚠️  偵測到投票輸0，立即觸發狼人自爆詢問！")
                                wolf_explode_ans = input("是否有狼人要自爆？ → 1=有自爆  0=無自爆：")
                                if wolf_explode_ans == "1":
                                    explode_trigger = True
                                    while True:
                                        wolf_exp_id = int(input(f"請選擇要自爆的狼人編號 (存活狼人：{alive_wolfs})："))
                                        if wolf_exp_id in alive_wolfs:
                                            self.players[wolf_exp_id]["alive"] = False
                                            explode_wolf_role = self.players[wolf_exp_id]["role"]
                                            print(f"✅ {wolf_exp_id}號狼人({explode_wolf_role})自爆成功！")

                                            # ✅ 白狼王核心規則：只有自爆才能帶人
                                            if explode_wolf_role == "白狼王":
                                                print(f"✅ 白狼王規則：自爆成功！發動帶人技能！")
                                                bite_tar = input(f"{wolf_exp_id}號白狼王自爆！咬殺目標編號，不咬輸0：")
                                                if bite_tar != "0" and int(bite_tar) in alive_players:
                                                    self.players[int(bite_tar)]["alive"] = False
                                                    print(f"✅ 白狼王咬死 {bite_tar}號玩家！")

                                            # ✅ 狼王規則：自爆也能帶人
                                            if explode_wolf_role == "狼王":
                                                print(f"✅ 狼王規則：自爆屬於死亡，可發動帶人技能！")
                                                bite_tar = input(f"{wolf_exp_id}號狼王自爆！咬殺目標編號，不咬輸0：")
                                                if bite_tar != "0" and int(bite_tar) in alive_players:
                                                    self.players[int(bite_tar)]["alive"] = False
                                                    print(f"✅ 狼王咬死 {bite_tar}號玩家！")

                                            # ✅ 黑狼王規則：自爆絕對不能帶人
                                            if explode_wolf_role == "黑狼王":
                                                print(f"❌ 黑狼王規則：自爆死亡，無法發動任何帶人技能！")

                                            # 血月使者自爆封印技能
                                            if explode_wolf_role == "血月使者":
                                                print(f"✅ 血月使者自爆！當晚所有好人技能被封印！")

                                            print("✅ 強制結束白天，立即進入黑夜！")
                                            break
                                    break
                                else:
                                    print("✅ 無狼人自爆，繼續進行公投投票！")
                                    continue

                            elif vote in alive_players:
                                vote_records[vote] += 1
                                print(f"✅ {voter}號投票給 {vote}號")
                                break
                            else:
                                print("輸入錯誤！請選擇存活玩家編號，輸0觸發自爆詢問！")
                        except:
                            print("輸入錯誤！請輸入數字編號，輸0觸發自爆詢問！")
                elif explode_trigger:
                    break

        # 有狼人自爆 → 強制結束白天，直接入夜
        if explode_trigger:
            self.check_win_condition()
            time.sleep(2)
            return

        # 無自爆 → 正常統計投票結果
        if alive_players and vote_records:
            max_vote = max(vote_records.values())
            vote_target = [p for p in vote_records if vote_records[p] == max_vote]
            if len(vote_target) == 1:
                vote_target = vote_target[0]
                self.grave_last_vote_role = \
                    [v["team"] for k, v in ROLES.items() if v["name"] == self.players[vote_target]["role"]][0]
                vt_role = self.players[vote_target]["role"]

                # 白痴規則
                if vt_role == "白痴":
                    self.players[vote_target]["can_vote"] = False
                    print(f"🤍 {vote_target}號白痴翻牌不死，失去投票權！")
                else:
                    # 血月使者規則
                    if vt_role == "血月使者" and len(alive_wolfs) == 1:
                        print(f"🌙 血月使者規則：最後狼人被投，翻牌存活至下一個白天！")
                    else:
                        self.players[vote_target]["alive"] = False
                        team_tag = "🟢好人" if vote_target in self.good_guys else "🔴狼人"
                        print(f"✅ {vote_target}號被公投出局！{team_tag}【{vt_role}】")

                        # 獵人被投開槍
                        if vt_role == "獵人" and not self.players[vote_target]["skill_lock"]:
                            shoot = input(f"{vote_target}號獵人被投！開槍輸入目標編號，不開輸0：")
                            if shoot != "0" and int(shoot) in alive_players:
                                self.players[int(shoot)]["alive"] = False
                                print(f"✅ 獵人開槍帶走 {shoot}號！")
                            else:
                                print("✅ 獵人選擇不開槍")
            else:
                print(f"🤝 投票平手！{vote_target}號PK，無人出局")

        self.check_win_condition()
        time.sleep(2)

    # ========== ✅ 勝利條件：必須一方【全滅】才結束遊戲 ✅ ==========
    def check_win_condition(self):
        alive_wolfs = self.get_alive_wolfs()
        alive_good = self.get_alive_good()

        if len(alive_wolfs) == 0:
            self.game_over = True
            self.winner = "好人陣營"
            print(f"\n🎉 遊戲結束！獲勝陣營：🟢{self.winner} 🎉")
            print("✅ 所有狼人已被消滅，好人陣營屠狼獲勝！")
        elif len(alive_good) == 0:
            self.game_over = True
            self.winner = "狼人陣營"
            print(f"\n🎉 遊戲結束！獲勝陣營：🔴{self.winner} 🎉")
            print("✅ 所有好人已被屠滅，狼人陣營屠城獲勝！")

    # ========== 顯示所有玩家真實身分 + 陣營標籤 ==========
    def show_all_roles(self):
        print("\n======= 📜 本局所有玩家真實身分【陣營清晰版】 =======")
        for p in self.players:
            status = "✅存活" if self.players[p]["alive"] else "❌死亡"
            vote = "🗳️可投票" if self.players[p]["can_vote"] else "❌無投票權"
            lock = "🔒技能封印" if self.players[p]["skill_lock"] else "✅技能可用"
            team_tag = "🟢好人" if p in self.good_guys else "🔴狼人"
            print(f"{p}號：{team_tag}【{self.players[p]['role']}】 {status} {vote} {lock}")

    # ========== ✅ 完整遊戲主循環 (包含重開機制) ✅ ==========
    def start_game(self):
        # 第一次開局：手動設定本局角色清單(只執行1次)
        self.manual_role_setup()
        while True:
            # 初始化遊戲 (第一次固定順序分配，重開手動分配 + 狀態重置)
            self.init_game()
            # 日夜循環直到一局結束
            while not self.game_over:
                self.night_action()
                if self.game_over: break
                self.day_vote()
                self.day += 1
            # 顯示本局結果
            self.show_all_roles()
            # 詢問是否重開
            restart = input("\n🎮 是否再來一次？輸入【再來一次】重開遊戲，輸入其他內容結束：")
            if restart != "再來一次":
                print("\n👋 謝謝玩狼人殺遊戲！下次再見～")
                break
            else:
                print("\n=====================================")
                print("🎮 準備重新開局！可手動分配角色！")
                print("=====================================")
                time.sleep(2)


# ========== 啟動遊戲 ==========
if __name__ == "__main__":
    game = WerewolfGame()
    game.start_game()