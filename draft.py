# draft.py
import discord
from discord.ui import View, Button, Select, Modal, TextInput
import re
from tiers import tier_database

# คะแนนอ้างอิงตามระดับ Tier
TIER_SCORES = {
    "SSS": 100,
    "SS": 92,
    "S": 85,
    "A+": 78,
    "A": 70,
    "B+": 62,
    "B": 55,
    "B-": 48,
    "เฉพาะทาง": 76
}

# ลำดับการดราฟต์ 2 โหมด
TOURNAMENT_STEPS = [
    ("BLUE", "BAN"), ("RED", "BAN"), ("BLUE", "BAN"), ("RED", "BAN"),
    ("BLUE", "PICK"), ("RED", "PICK"), ("RED", "PICK"), ("BLUE", "PICK"), ("BLUE", "PICK"), ("RED", "PICK"),
    ("RED", "BAN"), ("BLUE", "BAN"), ("RED", "BAN"), ("BLUE", "BAN"),
    ("RED", "PICK"), ("BLUE", "PICK"), ("BLUE", "PICK"), ("RED", "PICK")
]

RANKED_STEPS = [
    ("BLUE", "BAN"), ("RED", "BAN"), ("BLUE", "BAN"), ("RED", "BAN"), ("BLUE", "BAN"),
    ("RED", "BAN"), ("BLUE", "BAN"), ("RED", "BAN"), ("BLUE", "BAN"), ("RED", "BAN"),
    ("BLUE", "PICK"), ("RED", "PICK"), ("RED", "PICK"), ("BLUE", "PICK"), ("BLUE", "PICK"),
    ("RED", "PICK"), ("RED", "PICK"), ("BLUE", "PICK"), ("BLUE", "PICK"), ("RED", "PICK")
]

def parse_hero_data():
    hero_scores = {}
    role_heroes = {"all": []}
    role_labels = {"offlane": "DSL", "jungle": "JGL", "mage": "MID", "carry": "ADL", "support": "SUP"}
    
    for role, text in tier_database.items():
        role_heroes[role] = []
        for line in text.split("\n"):
            match = re.search(r'\*\*(.*?):\*\*\s*(.*)', line)
            if match:
                tier = match.group(1).strip()
                heroes_str = match.group(2).strip()
                if heroes_str == "-":
                    continue
                score = TIER_SCORES.get(tier, 65)
                for h in heroes_str.split(","):
                    name = h.strip()
                    if not name:
                        continue
                    if name not in hero_scores or score > hero_scores[name]["score"]:
                        hero_scores[name] = {"score": score, "tier": tier, "role": role_labels.get(role, role.upper())}
                    if name not in role_heroes[role]:
                        role_heroes[role].append(name)
                    if name not in role_heroes["all"]:
                        role_heroes["all"].append(name)
                        
    for r in role_heroes:
        role_heroes[r].sort(key=lambda x: hero_scores[x]["score"], reverse=True)
        
    return hero_scores, role_heroes

HERO_DATA, ROLE_HEROES = parse_hero_data()

class DraftSession:
    def __init__(self, mode="tournament"):
        self.mode = mode
        self.steps = TOURNAMENT_STEPS if mode == "tournament" else RANKED_STEPS
        self.step_idx = 0
        self.blue_bans = []
        self.red_bans = []
        self.blue_picks = []
        self.red_picks = []
        self.history = []
        self.filter_role = "all"

    @property
    def is_finished(self):
        return self.step_idx >= len(self.steps)

    @property
    def used_heroes(self):
        return set(self.blue_bans + self.red_bans + self.blue_picks + self.red_picks)

    def get_available_top5(self):
        used = self.used_heroes
        candidates = [h for h in ROLE_HEROES.get(self.filter_role, []) if h not in used]
        return candidates[:5]

    def apply_action(self, hero_name):
        if self.is_finished:
            return
        side, action = self.steps[self.step_idx]
        self.history.append((side, action, hero_name))
        if side == "BLUE" and action == "BAN":
            self.blue_bans.append(hero_name)
        elif side == "RED" and action == "BAN":
            self.red_bans.append(hero_name)
        elif side == "BLUE" and action == "PICK":
            self.blue_picks.append(hero_name)
        elif side == "RED" and action == "PICK":
            self.red_picks.append(hero_name)
        self.step_idx += 1

    def undo(self):
        if not self.history:
            return False
        side, action, hero_name = self.history.pop()
        if side == "BLUE" and action == "BAN":
            self.blue_bans.remove(hero_name)
        elif side == "RED" and action == "BAN":
            self.red_bans.remove(hero_name)
        elif side == "BLUE" and action == "PICK":
            self.blue_picks.remove(hero_name)
        elif side == "RED" and action == "PICK":
            self.red_picks.remove(hero_name)
        self.step_idx -= 1
        return True

    def calc_win_prob(self):
        blue_score = sum(HERO_DATA.get(h, {"score": 70})["score"] for h in self.blue_picks)
        red_score = sum(HERO_DATA.get(h, {"score": 70})["score"] for h in self.red_picks)
        blue_score += (5 - len(self.blue_picks)) * 75
        red_score += (5 - len(self.red_picks)) * 75
        total = blue_score + red_score
        blue_prob = round((blue_score / total) * 100, 1)
        red_prob = round(100 - blue_prob, 1)
        return blue_prob, red_prob

    def build_board_embed(self):
        blue_prob, red_prob = self.calc_win_prob()
        blue_blocks = int(round(blue_prob / 10))
        bar = "🟦" * blue_blocks + "🟥" * (10 - blue_blocks)

        mode_title = "TOURNAMENT (Ban 4 / Pick 5)" if self.mode == "tournament" else "RANKED (Ban 5 / Pick 5)"
        max_bans = 4 if self.mode == "tournament" else 5

        if not self.is_finished:
            side, action = self.steps[self.step_idx]
            side_icon = "🔵" if side == "BLUE" else "🔴"
            status_text = f"**STEP {self.step_idx + 1}/{len(self.steps)} : {side_icon} {side} {action}**"
            color = discord.Color.blue() if side == "BLUE" else discord.Color.red()
        else:
            status_text = "**🏁 DRAFT COMPLETED (จบการดราฟต์)**"
            color = discord.Color.gold()

        embed = discord.Embed(
            title=f"🏆 MINIDRAFT BOARD — {mode_title}",
            description=f"{status_text}\n\n**WIN PROBABILITY (โอกาสชนะทาง)**\n`BLUE {blue_prob}%` {bar} `{red_prob}% RED`",
            color=color
        )

        b_bans = [f"`B{i+1}:` {self.blue_bans[i] if i < len(self.blue_bans) else '*(ว่าง)*'}" for i in range(max_bans)]
        b_picks = [f"`{i+1}.` {self.blue_picks[i] if i < len(self.blue_picks) else '*(ว่าง)*'}" for i in range(5)]
        embed.add_field(
            name="🔵 BLUE TEAM",
            value="**🚫 BAN:**\n" + "\n".join(b_bans) + "\n\n**⚔️ PICK:**\n" + "\n".join(b_picks),
            inline=True
        )

        r_bans = [f"`B{i+1}:` {self.red_bans[i] if i < len(self.red_bans) else '*(ว่าง)*'}" for i in range(max_bans)]
        r_picks = [f"`{i+1}.` {self.red_picks[i] if i < len(self.red_picks) else '*(ว่าง)*'}" for i in range(5)]
        embed.add_field(
            name="🔴 RED TEAM",
            value="**🚫 BAN:**\n" + "\n".join(r_bans) + "\n\n**⚔️ PICK:**\n" + "\n".join(r_picks),
            inline=True
        )

        if not self.is_finished:
            top5 = self.get_available_top5()
            rec_list = [f"`#{i+1}` **{h}** ({HERO_DATA[h]['role']} - {HERO_DATA[h]['tier']})" for i, h in enumerate(top5)]
            embed.add_field(
                name="💡 PRIORITY แนะนำ (กดปุ่มหรือค้นหาชื่อ):",
                value=" | ".join(rec_list) if rec_list else "ไม่มีข้อมูล",
                inline=False
            )
        else:
            analysis_text = self.generate_post_draft_analysis(blue_prob, red_prob)
            embed.add_field(name="📊 ผลการวิเคราะห์หลังดราฟต์ (Post-Draft Analysis)", value=analysis_text, inline=False)

        return embed

    def generate_post_draft_analysis(self, blue_prob, red_prob):
        early_heroes = {"Nakroth", "Aoi", "Keera", "Zuka", "Ryoma", "Valhein", "Stuart", "Elsu", "Tulen", "Raz", "Krizzix", "TeeMee", "Biron", "Florentino"}
        late_heroes = {"Violet", "Capheny", "Tel'Annas", "Hayate", "Yorn", "Laville", "Thorne", "Lauriel", "Liliana", "Yue", "Dolia", "Marja", "Taara", "Omen"}
        teamfight_heroes = {"Y'bneth", "Dolia", "Maloch", "Thane", "Toro", "Baldum", "Gildur", "Lorion", "Dirak", "Iggy", "Ignis", "Zata", "Annette", "Rouie", "Evita"}

        b_early = len(set(self.blue_picks) & early_heroes)
        r_early = len(set(self.red_picks) & early_heroes)
        b_late = len(set(self.blue_picks) & late_heroes)
        r_late = len(set(self.red_picks) & late_heroes)
        b_tf = len(set(self.blue_picks) & teamfight_heroes)
        r_tf = len(set(self.red_picks) & teamfight_heroes)

        tf_blue = min(85, max(15, round(50 + (b_tf - r_tf) * 7 + (blue_prob - 50) * 0.5, 1)))
        tf_red = round(100 - tf_blue, 1)

        if b_late > b_early and r_early >= 2:
            danger_blue = "🔴 **ช่วงต้นเกม (นาทีที่ 1 - 6)** ระวังโดนฝั่งแดงบุกป่าและกดดันหนัก"
        elif b_early > b_late and r_late >= 2:
            danger_blue = "🟠 **ช่วงเลทเกม (นาทีที่ 15 ขึ้นไป)** ต้องรีบปิดเกม หากปล่อยให้เลทเกมฝั่งตรงข้ามสู้ยาก"
        else:
            danger_blue = "🟡 **ช่วงกลางเกม (นาทีที่ 8 - 13)** ไฟต์ชี้ขาดหน้ามังกรใหญ่/สเลเยอร์ สำคัญมาก"

        return (
            f"• **% ชนะทางรวม:** 🔵 Blue `{blue_prob}%` vs 🔴 Red `{red_prob}%`\n"
            f"• **⚔️ โอกาสชนะทีมไฟต์:** 🔵 Blue `{tf_blue}%` vs 🔴 Red `{tf_red}%`\n"
            f"• **⚠️ ช่วงเวลาที่เสี่ยงแพ้ (Blue Team):** {danger_blue}"
        )


class HeroSearchModal(Modal, title="🔍 ค้นหาชื่อฮีโร่"):
    query_input = TextInput(label="ชื่อฮีโร่ (พิมพ์ตัวย่อได้)", placeholder="เช่น nak, dolia, hayate", min_length=1, max_length=30)

    def __init__(self, board_view):
        super().__init__()
        self.board_view = board_view

    async def on_submit(self, interaction: discord.Interaction):
        query = self.query_input.value.strip().lower()
        used = self.board_view.session.used_heroes
        available = [h for h in ROLE_HEROES["all"] if h not in used]

        exact = [h for h in available if h.lower() == query]
        if exact:
            self.board_view.session.apply_action(exact[0])
            self.board_view.update_components()
            await interaction.response.edit_message(embed=self.board_view.session.build_board_embed(), view=self.board_view)
            return

        starts_with = [h for h in available if h.lower().startswith(query)]
        contains = [h for h in available if query in h.lower() and h not in starts_with]
        matches = starts_with + contains

        if not matches:
            await interaction.response.send_message(f"❌ ไม่พบฮีโร่ `{self.query_input.value}`", ephemeral=True)
        elif len(matches) == 1:
            self.board_view.session.apply_action(matches[0])
            self.board_view.update_components()
            await interaction.response.edit_message(embed=self.board_view.session.build_board_embed(), view=self.board_view)
        else:
            await interaction.response.send_message(
                f"🔎 พบฮีโร่คล้าย `{self.query_input.value}` เลือกตัวที่ต้องการ:",
                view=DisambiguateView(self.board_view, matches[:10]),
                ephemeral=True
            )


class DisambiguateView(View):
    def __init__(self, board_view, candidates):
        super().__init__(timeout=60)
        self.board_view = board_view
        for hero in candidates:
            btn = Button(label=hero, style=discord.ButtonStyle.primary)
            btn.callback = self.make_callback(hero)
            self.add_item(btn)

    def make_callback(self, hero_name):
        async def callback(interaction: discord.Interaction):
            if hero_name in self.board_view.session.used_heroes:
                await interaction.response.edit_message(content=f"⚠️ **{hero_name}** ถูกเลือกไปแล้ว", view=None)
                return
            self.board_view.session.apply_action(hero_name)
            self.board_view.update_components()
            await interaction.response.edit_message(content=f"✅ เลือก **{hero_name}** สำเร็จ!", view=None)
            await self.board_view.message.edit(embed=self.board_view.session.build_board_embed(), view=self.board_view)
        return callback


class DraftBoardView(View):
    def __init__(self, mode="tournament"):
        super().__init__(timeout=900)
        self.session = DraftSession(mode=mode)
        self.message = None
        self.update_components()

    def update_components(self):
        self.clear_items()
        if not self.session.is_finished:
            role_select = Select(
                placeholder="🔽 กรองตำแหน่งแนะนำ...",
                options=[
                    discord.SelectOption(label="ทุกสาย (ALL)", value="all", default=(self.session.filter_role == "all")),
                    discord.SelectOption(label="DSL ออฟเลน", value="offlane", default=(self.session.filter_role == "offlane")),
                    discord.SelectOption(label="JGL ป่า", value="jungle", default=(self.session.filter_role == "jungle")),
                    discord.SelectOption(label="MID เมจ", value="mage", default=(self.session.filter_role == "mage")),
                    discord.SelectOption(label="ADL แครี่", value="carry", default=(self.session.filter_role == "carry")),
                    discord.SelectOption(label="SUP โรมมิ่ง", value="support", default=(self.session.filter_role == "support")),
                ],
                row=0
            )
            role_select.callback = self.on_role_change
            self.add_item(role_select)

            top5 = self.session.get_available_top5()
            for i, hero in enumerate(top5):
                btn = Button(label=f"#{i+1} {hero}", style=discord.ButtonStyle.secondary, row=1)
                btn.callback = self.make_quick_pick(hero)
                self.add_item(btn)

            search_btn = Button(label="🔍 พิมพ์ค้นหาฮีโร่", style=discord.ButtonStyle.primary, row=2)
            search_btn.callback = self.on_search
            self.add_item(search_btn)

        undo_btn = Button(label="↩️ ย้อนกลับ", style=discord.ButtonStyle.secondary, row=2, disabled=(len(self.session.history) == 0))
        undo_btn.callback = self.on_undo
        self.add_item(undo_btn)

        reset_btn = Button(label="🔄 เริ่มใหม่", style=discord.ButtonStyle.danger, row=2)
        reset_btn.callback = self.on_reset
        self.add_item(reset_btn)

    async def on_role_change(self, interaction: discord.Interaction):
        self.session.filter_role = interaction.data["values"][0]
        self.update_components()
        await interaction.response.edit_message(embed=self.session.build_board_embed(), view=self)

    def make_quick_pick(self, hero_name):
        async def callback(interaction: discord.Interaction):
            self.session.apply_action(hero_name)
            self.update_components()
            await interaction.response.edit_message(embed=self.session.build_board_embed(), view=self)
        return callback

    async def on_search(self, interaction: discord.Interaction):
        await interaction.response.send_modal(HeroSearchModal(self))

    async def on_undo(self, interaction: discord.Interaction):
        self.session.undo()
        self.update_components()
        await interaction.response.edit_message(embed=self.session.build_board_embed(), view=self)

    async def on_reset(self, interaction: discord.Interaction):
        self.session = DraftSession(mode=self.session.mode)
        self.update_components()
        await interaction.response.edit_message(embed=self.session.build_board_embed(), view=self)


class ModeSelectView(View):
    def __init__(self):
        super().__init__(timeout=120)

    @discord.ui.button(label="🏆 โหมดแข่ง (แบน 4 เลือก 5)", style=discord.ButtonStyle.primary)
    async def tourney_btn(self, interaction: discord.Interaction, button: Button):
        board = DraftBoardView(mode="tournament")
        await interaction.response.edit_message(content=None, embed=board.session.build_board_embed(), view=board)
        board.message = await interaction.original_response()

    @discord.ui.button(label="⚔️ โหมดแรงค์ (แบน 5 เลือก 5)", style=discord.ButtonStyle.success)
    async def ranked_btn(self, interaction: discord.Interaction, button: Button):
        board = DraftBoardView(mode="ranked")
        await interaction.response.edit_message(content=None, embed=board.session.build_board_embed(), view=board)
        board.message = await interaction.original_response()
