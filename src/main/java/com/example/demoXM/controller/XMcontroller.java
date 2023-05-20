package com.example.demoXM.controller;

import java.util.List;

import javax.servlet.http.HttpSession;

import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Controller;
import org.springframework.ui.Model;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;

import com.example.demoXM.entity.Hoken;
import com.example.demoXM.helper.SessionHelper;
import com.example.demoXM.service.HokenService;

@Controller
@RequestMapping("/top")
public class XMcontroller {
	@Autowired
	private HokenService hokenService;

	//	//展示top页面
	//	@GetMapping("/show")
	//	public String show() {
	//		return "A1A01WA01A01_TOP画面";
	//	}
	//展示お勧め页面
	//	@GetMapping("/show2")
	//	public String show2() {
	//		return "A1A01WA01A02_お勧め保険一覧";
	//	}
	//跳转到登陆页面
	@GetMapping("/show3")
	public String show3() {
		return "B1A01WA01A01_登録画面";
	}

	//新规跳转入会申请情报入力
	@GetMapping("/new")
	public String apply() {
		return "B1A01WA02A01_入会申込情報入力";
	}

	//未登录的情况

	//登陆的情况/top/show?id=1
	@GetMapping("/show")
	//把value的id拿到 给下面的integer id
	public String show(@RequestParam(name = "id", required = false) Integer id, Model model, HttpSession session) {
		String role = SessionHelper.getSessionRole(session);
		model.addAttribute("id", role);
		//点击id==1点击ご会員 就跳转a
		return "A1A01WA01A01_TOP画面";
		//如果是社员 就跳转到b
		//		return "F1E01WA01A01_会員情報照会検索";
	}

	//id=1时跳转的社员页面
	@GetMapping("/sheyuan")
	public String sheyuan() {
		return "F1E01WA01A01_会員情報照会検索";
	}

	//id=0时跳转的会员页面
	@GetMapping("/huiyuan")
	public String huiyuan() {
		return "C1C03WC01A01_個人情報照会";
	}

	//是社员跳转到保险情报搜索
	@GetMapping("/baoxiansousuo")
	public String baoxiansousuo(Model model) {
		List<Hoken> list2 = hokenService.selectHoken(null, null, null, null, null);
		for (Hoken hoken : list2) {
			if (hoken.getHBKB().equals("1")) {
				hoken.setHBKB("すべて");
			} else if (hoken.getHBKB().equals("2")) {
				hoken.setHBKB("オンライン");
			} else {
				hoken.setHBKB("店頭");
			}
			if (hoken.getSTS().equals("1")) {
				hoken.setSTS("準備中");
			} else if (hoken.getSTS().equals("2")) {
				hoken.setSTS("有効");
			} else {
				hoken.setSTS("無効");
			}
		}
		model.addAttribute("select", list2);
		return "E1F01WA02A01_保険情報検索";
	}

	//带值搜索
	@PostMapping("/baoxiansousuo")
	public String selectHoken(Model model, String HKID, String HKN, String HKKTKB, String HBKB, String STS) {
		System.out.println(HBKB);
		System.out.println(STS);
		List<Hoken> list3 = hokenService.selectHoken(HKID, HKN, HKKTKB, HBKB, STS);
		for (Hoken hoken : list3) {
			System.out.println(hoken);
		}
		model.addAttribute("select", list3);
		return "E1F01WA02A01_保険情報検索";
	}
	//
	//	//是会员跳转到お勧め保险
	//		@GetMapping("/osusume")
	//		public String osusume() {
	//			return "A1A01WA01A02_お勧め保険一覧";
	//		}

	//带保险信息
	@GetMapping("/osusume")
	public String baoxian(Model model, @RequestParam String sex) {
		List<Hoken> list = hokenService.getHoken(sex);
		for (Hoken hoken1 : list) {
			if (hoken1.getHBFLG().equals("1")) {
				hoken1.setHBFLG("可");
			} else {
				hoken1.setHBFLG("不可");
			}
			if (hoken1.getKTKYFLG().equals("1")) {
				hoken1.setKTKYFLG("可");
			} else {
				hoken1.setKTKYFLG("不可");
			}
		}
		model.addAttribute("osusume", list);
		return "A1A01WA01A02_お勧め保険一覧";
	}

	//跳转到新规
	@GetMapping("/xin")
	public String xingui(@RequestBody Hoken hoken) {
		return "E1F01WA01A04_保険情報登録変更";
	}

}
